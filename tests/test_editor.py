from __future__ import annotations

import io
import json
import runpy
import shutil
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from editor import create_app
from editor.__main__ import DEFAULT_PORT, parse_args
from editor.quality import KnowledgeQualityCenter, QualityRegistry
from editor.quality.models import ChecklistItem, CheckResult, QualityContext
from scripts.generate_seed import ONTOLOGY_DIR

CANONICAL_FILES = ("macroareas.json", "areas.json", "subareas.json")


def test_editor_port_defaults_and_override() -> None:
    assert DEFAULT_PORT == 7777
    assert parse_args([]).port == 7777
    assert parse_args(["--port", "8888"]).port == 8888


def _editor_client(tmp_path: Path) -> tuple[TestClient, Path]:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir()
    for filename in CANONICAL_FILES:
        shutil.copyfile(ONTOLOGY_DIR / filename, ontology_dir / filename)
    shutil.copyfile(ONTOLOGY_DIR / "seed_compressed.py", ontology_dir / "seed_compressed.py")
    return TestClient(create_app(ontology_dir)), ontology_dir


def _flatten_tree(nodes: list[dict[str, object]]) -> list[dict[str, object]]:
    flattened: list[dict[str, object]] = []
    for node in nodes:
        flattened.append(node)
        flattened.extend(_flatten_tree(node["children"]))  # type: ignore[arg-type]
    return flattened


def _tree_ids(nodes: list[dict[str, object]]) -> set[str]:
    return {str(node["id"]) for node in _flatten_tree(nodes)}


def _node_payload(
    identifier: str,
    label: str,
    node_type: str = "macroarea",
    parent_id: str | None = None,
) -> dict[str, object]:
    return {
        "id": identifier,
        "type": node_type,
        "label": label,
        "description": f"Descrizione di {label}",
        "parent_id": parent_id,
        "language": "it",
    }


def _import_preview(
    client: TestClient,
    filename: str,
    content: str | bytes,
    mode: str = "assisted",
    mappings: dict[str, str] | None = None,
    persist_mappings: bool = False,
) -> dict[str, object]:
    raw = content.encode("utf-8") if isinstance(content, str) else content
    response = client.post(
        "/api/import/preview",
        params={
            "filename": filename,
            "mode": mode,
            "mappings": json.dumps(mappings or {}),
            "persist_mappings": str(persist_mappings).lower(),
        },
        content=raw,
        headers={"Content-Type": "application/octet-stream"},
    )
    assert response.status_code == 200
    return response.json()


def test_tree_loading(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    response = client.get("/api/tree")

    assert response.status_code == 200
    tree = response.json()
    assert len(tree) == 48
    assert len(_flatten_tree(tree)) == 1229
    assert tree[0]["id"] == "agricoltura"
    assert tree[0]["children"]


def test_node_api_exposes_editor_metadata(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    response = client.get("/api/node/mat_algebra")

    assert response.status_code == 200
    node = response.json()
    assert node["type"] == "area"
    assert node["parent_id"] == "matematica"
    assert node["children_count"] > 0
    assert node["descendants_count"] == node["children_count"]
    assert node["child_type"] == "sottoarea"
    assert node["child_creation_supported"] is True
    assert [item["id"] for item in node["path"]] == ["matematica", "mat_algebra"]


def test_context_aware_child_types(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    macroarea = client.get("/api/node/matematica").json()
    area = client.get("/api/node/mat_algebra").json()
    subarea = client.get("/api/node/mat_al_equazioni").json()

    assert (macroarea["child_type"], macroarea["child_creation_supported"]) == ("area", True)
    assert (area["child_type"], area["child_creation_supported"]) == ("sottoarea", True)
    assert (subarea["child_type"], subarea["child_creation_supported"]) == (
        "concetto",
        False,
    )


def test_id_suggestion_normalization_and_collision(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    normalized = client.get(
        "/api/suggest-id",
        params={
            "parent_id": "mat_algebra",
            "label": "Équazioni -- differenziali!",
        },
    )
    collision = client.get("/api/suggest-id", params={"label": "Matematica"})

    assert normalized.json() == {
        "id": "mat_algebra_equazioni_differenziali",
        "collision": False,
    }
    assert collision.json() == {"id": "matematica_2", "collision": True}


def test_tree_search_preserves_ancestors_and_ignores_accents(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    response = client.get("/api/tree", params={"q": "li_st_origini"})
    accent_response = client.get("/api/tree", params={"q": "attualita"})

    assert response.status_code == 200
    assert _tree_ids(response.json()) == {
        "lingua_italiana",
        "li_storia",
        "li_st_origini",
    }
    assert "attualita_societa" in _tree_ids(accent_response.json())


def test_tree_orders_siblings_by_italian_label_and_preserves_hierarchy(
    tmp_path: Path,
) -> None:
    client, _ = _editor_client(tmp_path)
    for payload in (
        _node_payload("sort_z", "Zeta"),
        _node_payload("sort_a", "albero"),
        _node_payload("sort_accent", "Ètica"),
        _node_payload("sort_e", "etica"),
        _node_payload("sort_parent", "Famiglia"),
        _node_payload("sort_child_z", "Zaino", "area", "sort_parent"),
        _node_payload("sort_child_a", "Àlgebra", "area", "sort_parent"),
    ):
        assert client.post("/api/node", json=payload).status_code == 201

    tree = client.get("/api/tree").json()
    root_ids = [node["id"] for node in tree if node["id"].startswith("sort_")]
    parent = next(node for node in tree if node["id"] == "sort_parent")

    assert root_ids == ["sort_a", "sort_accent", "sort_e", "sort_parent", "sort_z"]
    assert [child["id"] for child in parent["children"]] == [
        "sort_child_a",
        "sort_child_z",
    ]
    assert all(child["id"] not in root_ids for child in parent["children"])


def test_tree_uses_type_and_id_for_duplicate_labels_and_reorders_after_update(
    tmp_path: Path,
) -> None:
    client, _ = _editor_client(tmp_path)
    for payload in (
        _node_payload("sort_duplicate_b", "Uguale"),
        _node_payload("sort_duplicate_a", "Uguale"),
        _node_payload("sort_update", "Zuzzurellone"),
    ):
        assert client.post("/api/node", json=payload).status_code == 201

    initial = client.get("/api/tree").json()
    duplicates = [node["id"] for node in initial if node["label"] == "Uguale"]
    assert duplicates == ["sort_duplicate_a", "sort_duplicate_b"]

    payload = _node_payload("sort_update", "Abaco")
    assert client.put("/api/node/sort_update", json=payload).status_code == 200
    updated = client.get("/api/tree").json()
    labels = [node["label"] for node in updated]
    assert labels.index("Abaco") < labels.index("Uguale")


def test_editor_applies_italian_label_sorting_to_all_ui_collections(
    tmp_path: Path,
) -> None:
    client, _ = _editor_client(tmp_path)

    app_js = client.get("/static/app.js").text

    assert 'new Intl.Collator("it"' in app_js
    assert 'sensitivity: "base"' in app_js
    assert "compareByVisibleLabel(left.value, right.value)" in app_js
    assert "sortTreeForDisplay(tree)" in app_js
    assert "stableLabelSort(state.nodes)" in app_js


def test_api_can_create_update_and_delete_a_node(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    payload = {
        "id": "test_macroarea",
        "type": "macroarea",
        "label": "Test",
        "description": "Macroarea temporanea per il test",
        "parent_id": None,
        "language": "it",
    }

    created = client.post("/api/node", json=payload)
    assert created.status_code == 201
    assert client.post("/api/node", json=payload).status_code == 409

    payload["label"] = "Test aggiornato"
    updated = client.put("/api/node/test_macroarea", json=payload)
    assert updated.status_code == 200
    assert updated.json()["label"] == "Test aggiornato"
    assert "test_macroarea" in _tree_ids(client.get("/api/tree").json())

    deleted = client.delete("/api/node/test_macroarea")
    assert deleted.status_code == 204
    assert client.get("/api/node/test_macroarea").status_code == 404


def test_delete_protection_reports_descendants(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    node = client.get("/api/node/matematica").json()

    response = client.delete("/api/node/matematica")

    assert node["descendants_count"] > 0
    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot delete a node that has children"


def test_validation_status_api_reports_valid_working_copy(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    response = client.post("/api/validate")

    assert response.status_code == 200
    assert response.json() == {"valid": True, "errors": []}


def test_save_writes_valid_canonical_data_and_generated_seed(tmp_path: Path) -> None:
    client, ontology_dir = _editor_client(tmp_path)
    node = client.get("/api/node/mat_algebra").json()
    node["description"] = "Descrizione aggiornata dal test"
    payload = {
        field: node[field]
        for field in ("id", "type", "label", "description", "parent_id", "language")
    }

    assert client.put("/api/node/mat_algebra", json=payload).status_code == 200
    response = client.post("/api/save")

    assert response.status_code == 200
    assert response.json() == {"valid": True, "errors": [], "saved": True}
    areas = json.loads((ontology_dir / "areas.json").read_text(encoding="utf-8"))
    saved = next(record for record in areas if record["id"] == "mat_algebra")
    assert saved["description"] == "Descrizione aggiornata dal test"
    generated = runpy.run_path(str(ontology_dir / "seed_compressed.py"))
    assert sum(len(children) for _, children in generated["AREAS"]) == 471


def test_failed_validation_does_not_write_files(tmp_path: Path) -> None:
    client, ontology_dir = _editor_client(tmp_path)
    before = {
        filename: (ontology_dir / filename).read_bytes()
        for filename in (*CANONICAL_FILES, "seed_compressed.py")
    }
    node = client.get("/api/node/mat_algebra").json()
    payload = {
        field: node[field]
        for field in ("id", "type", "label", "description", "parent_id", "language")
    }
    payload["parent_id"] = "missing_parent"
    assert client.put("/api/node/mat_algebra", json=payload).status_code == 200

    validation = client.post("/api/validate")
    save = client.post("/api/save")

    assert validation.status_code == 200
    assert validation.json()["valid"] is False
    assert validation.json()["errors"] == ["mat_algebra: missing parent missing_parent"]
    assert save.status_code == 422
    assert save.json()["saved"] is False
    after = {
        filename: (ontology_dir / filename).read_bytes()
        for filename in (*CANONICAL_FILES, "seed_compressed.py")
    }
    assert after == before


def test_json_import_preview_and_confirm(tmp_path: Path) -> None:
    client, ontology_dir = _editor_client(tmp_path)
    payload = {
        "nodes": [
            {
                "id": "imported.topic",
                "type": "macroarea",
                "label": "Importata",
                "description": "Macroarea importata",
                "parent": None,
            },
            {
                "id": "imported.topic.area",
                "type": "area",
                "label": "Area importata",
                "description": "Area importata dal test",
                "parent": "imported.topic",
            },
            {
                "id": "imported.topic.area.category",
                "type": "categoria",
                "label": "Categoria importata",
                "description": "Sottoarea importata dal test",
                "parent": "imported.topic.area",
                "keywords": ["test"],
            },
        ]
    }

    result = _import_preview(client, "ontology.json", json.dumps(payload))
    assert result["format"] == "json"
    assert result["nodes_found"] == 3
    assert result["nodes_to_add"] == 3
    assert result["relationships_found"] == 2
    assert result["importable"] is True
    assert "ID 'imported.topic' → 'imported_topic'" in result["modifications"]
    assert "imported.topic.area.category: type 'categoria' → 'sottoarea'" in result["modifications"]
    assert result["warnings"] == [
        "imported.topic.area.category: ignored non-canonical fields: keywords"
    ]

    warning_ids = [warning["id"] for warning in result["warning_options"]]
    confirmed = client.post(
        "/api/import/confirm",
        json={"token": result["token"], "accepted_warnings": warning_ids},
    )

    report = confirmed.json()["report"]
    assert report["format"] == "json"
    assert report["parser"] == "json"
    assert report["summary"] == {"nodes_added": 3, "relationships_added": 2}
    assert report["warnings_handled"] == result["warnings"]
    assert report["files_modified"][-1] == "ontology/seed_compressed.py"
    macroareas = json.loads((ontology_dir / "macroareas.json").read_text(encoding="utf-8"))
    areas = json.loads((ontology_dir / "areas.json").read_text(encoding="utf-8"))
    subareas = json.loads((ontology_dir / "subareas.json").read_text(encoding="utf-8"))
    assert macroareas[-1]["id"] == "imported_topic"
    assert areas[-1]["parent_id"] == "imported_topic"
    assert subareas[-1]["parent_id"] == "imported_topic_area"
    assert runpy.run_path(str(ontology_dir / "seed_compressed.py"))["MACROAREAS"][-1][0] == (
        "imported_topic"
    )


def test_import_preview_reports_duplicates_and_collisions(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    nodes = [
        {
            "id": "matematica",
            "type": "macroarea",
            "label": "Matematica diversa",
            "description": "Conflitto intenzionale",
            "parent": None,
        },
        {
            "id": "lingua_italiana",
            "type": "macroarea",
            "label": "Lingua italiana",
            "description": "Storia, normativa, uso e varietà della lingua italiana",
            "parent": None,
        },
    ]

    result = _import_preview(client, "nodes.json", json.dumps(nodes))

    assert result["importable"] is False
    assert result["token"] is None
    assert result["collisions"] == ["matematica"]
    assert result["duplicates"] == ["lingua_italiana"]
    assert result["errors"] == ["matematica: conflicts with an existing canonical node"]


def test_kimi_parser_is_static_and_requests_unknown_type_mapping(tmp_path: Path) -> None:
    client, ontology_dir = _editor_client(tmp_path)
    marker = ontology_dir / "must_not_exist"
    source = f"""
from pathlib import Path
Path({str(marker)!r}).write_text("executed")
nodes = {{}}
children_map = defaultdict(list)
add_node("safe.root", "Radice", "Descrizione", None, "macroarea")
ONTO = {{
    "branch": {{
        "label": "Ramo",
        "desc": "Descrizione ramo",
        "type": "argomento",
    }}
}}
expand("safe.root", ONTO)
"""

    result = _import_preview(client, "kimi.py", source)

    assert result["format"] == "python"
    assert result["parser"] == "kimi-python"
    assert result["nodes_found"] == 2
    assert result["importable"] is False
    assert result["unmapped_types"] == ["argomento"]
    assert result["errors"] == []
    assert not marker.exists()


def test_import_confirmation_token_is_single_use(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    content = json.dumps(
        [
            {
                "id": "single_use",
                "type": "macroarea",
                "label": "Uso singolo",
                "description": "Verifica token monouso",
                "parent": None,
            }
        ]
    )
    preview = _import_preview(client, "single.json", content)

    assert client.post("/api/import/confirm", json={"token": preview["token"]}).status_code == 200
    repeated = client.post("/api/import/confirm", json={"token": preview["token"]})
    assert repeated.status_code == 404


def test_import_requires_explicit_data_loss_warning_acknowledgement(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    content = json.dumps(
        [
            {
                "id": "warning_node",
                "type": "macroarea",
                "label": "Warning",
                "description": "Nodo con metadato non canonico",
                "parent": None,
                "external_metadata": "presente",
            }
        ]
    )
    preview = _import_preview(client, "warning.json", content, mode="automatic")

    rejected = client.post("/api/import/confirm", json={"token": preview["token"]})
    accepted = client.post(
        "/api/import/confirm",
        json={
            "token": preview["token"],
            "mode": "automatic",
            "accepted_warnings": [preview["warning_options"][0]["id"]],
        },
    )

    assert rejected.status_code == 409
    assert "must be acknowledged" in rejected.json()["detail"]
    assert accepted.status_code == 200


def test_yaml_import_parser(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    content = """
nodes:
  - id: yaml_root
    type: macroarea
    label: Radice YAML
    description: Importazione YAML
    parent: null
"""

    result = _import_preview(client, "ontology.yaml", content)

    assert result["format"] == "yaml"
    assert result["parser"] == "yaml-internal"
    assert result["nodes_found"] == 1
    assert result["importable"] is True


def test_import_preview_is_deterministic_except_for_confirmation_token(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    content = """
- id: deterministic_root
  type: macroarea
  label: Radice deterministica
  description: Anteprima ripetibile
  parent: null
"""

    first = _import_preview(client, "deterministic.yml", content)
    second = _import_preview(client, "deterministic.yml", content)
    first.pop("token")
    second.pop("token")

    assert first == second


def test_mapping_created_in_preview_is_persisted_and_reused(tmp_path: Path) -> None:
    client, ontology_dir = _editor_client(tmp_path)
    content = json.dumps(
        [
            {
                "id": "mapped_root",
                "type": "external_root",
                "label": "Radice",
                "description": "Radice esterna",
                "parent": None,
            },
            {
                "id": "mapped_area",
                "type": "external_branch",
                "label": "Ramo",
                "description": "Ramo esterno",
                "parent": "mapped_root",
            },
            {
                "id": "mapped_leaf",
                "type": "external_leaf",
                "label": "Foglia",
                "description": "Foglia esterna",
                "parent": "mapped_area",
            },
        ]
    )
    initial = _import_preview(client, "mapped.json", content)

    assert initial["unmapped_types"] == [
        "external_branch",
        "external_leaf",
        "external_root",
    ]
    assert initial["errors"] == []

    mappings = {
        "external_root": "macroarea",
        "external_branch": "area",
        "external_leaf": "sottoarea",
    }
    mapped = _import_preview(
        client,
        "mapped.json",
        content,
        mappings=mappings,
        persist_mappings=True,
    )
    repeated = _import_preview(client, "mapped.json", content)
    confirmed = client.post("/api/import/confirm", json={"token": mapped["token"]})

    assert mapped["importable"] is True
    assert mapped["unmapped_types"] == []
    assert repeated["importable"] is True
    saved = json.loads((ontology_dir / "import_mappings.json").read_text(encoding="utf-8"))
    assert {key: saved[key] for key in mappings} == mappings
    assert "ontology/import_mappings.json" in confirmed.json()["report"]["files_modified"]


def test_mapped_type_still_blocks_when_hierarchy_cannot_be_represented(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    content = json.dumps(
        [
            {
                "id": "invalid_root",
                "type": "macroarea",
                "label": "Radice",
                "description": "Radice",
                "parent": None,
            },
            {
                "id": "invalid_category",
                "type": "categoria",
                "label": "Categoria",
                "description": "Categoria",
                "parent": "invalid_root",
            },
            {
                "id": "invalid_concept",
                "type": "concetto",
                "label": "Concetto",
                "description": "Concetto",
                "parent": "invalid_category",
            },
        ]
    )

    result = _import_preview(
        client,
        "invalid.json",
        content,
        mappings={"concetto": "sottoarea"},
    )

    assert result["unmapped_types"] == []
    assert result["importable"] is False
    assert any("invalid hierarchy" in error for error in result["errors"])


def test_quality_center_report_is_deterministic_and_navigable(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    first = client.get("/api/quality/report")
    second = client.get("/api/quality/report")

    assert first.status_code == 200
    assert first.json() == second.json()
    report = first.json()
    assert 0 <= report["score"] <= 100
    assert set(report["dimensions"]) == {
        "completezza",
        "integrità",
        "coerenza",
        "documentazione",
        "copertura",
    }
    assert report["statistics"]["nodes"] == 1229
    assert report["statistics"]["relationships"] == 1181
    assert report["errors"] == []
    assert len(report["checklist"]) == 5
    tree_ids = _tree_ids(client.get("/api/tree").json())
    assert all(
        issue["node_id"] in tree_ids for issue in report["warnings"] if issue["node_id"] is not None
    )


def test_quality_center_is_served_as_an_independent_window(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    editor_html = client.get("/").text
    quality_html = client.get("/static/quality.html")
    quality_js = client.get("/static/quality.js")
    quality_css = client.get("/static/quality.css")

    assert quality_html.status_code == 200
    assert quality_js.status_code == 200
    assert quality_css.status_code == 200
    assert 'id="quality-dialog"' not in editor_html
    assert "Knowledge Quality Center" in quality_html.text
    assert 'fetch("/api/quality/report"' in quality_js.text
    assert "window.setInterval(loadReport, 2000)" in quality_js.text
    assert "ikg:navigate-node" in quality_js.text
    assert ".score-layout" in quality_css.text
    assert 'id="prepare-contribution"' in editor_html
    assert 'id="contribution-dialog"' in editor_html
    assert 'request("/api/contribution/preview")' in client.get("/static/app.js").text


def test_editor_layout_uses_independent_25_75_scrolling_panels(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    styles = client.get("/static/styles.css").text

    assert "grid-template-columns: minmax(240px, 25%) minmax(0, 75%);" in styles
    assert ".editor-panel {" in styles
    assert "overflow-y: auto;" in styles
    assert "body {" in styles
    assert "overflow: hidden;" in styles
    assert ".form-actions {" in styles
    assert "position: sticky;" in styles


def test_quality_center_reports_integrity_error_and_session_activity(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    node = client.get("/api/node/mat_algebra").json()
    payload = {
        field: node[field]
        for field in ("id", "type", "label", "description", "parent_id", "language")
    }
    payload["parent_id"] = "missing_quality_parent"

    assert client.put("/api/node/mat_algebra", json=payload).status_code == 200
    report = client.get("/api/quality/report").json()

    assert report["score"] < 100
    assert any(issue["node_id"] == "mat_algebra" for issue in report["errors"])
    assert report["activity"][-1]["action"] == "update"
    assert report["activity"][-1]["node_id"] == "mat_algebra"


def test_quality_registry_accepts_new_checks_without_core_changes() -> None:
    class CustomCheck:
        identifier = "quality.custom"

        def evaluate(self, context: QualityContext) -> CheckResult:
            return CheckResult(
                "personalizzata",
                75.0,
                (),
                (ChecklistItem("quality.custom", "Controllo esterno", True),),
            )

    registry = QualityRegistry()
    registry.register(CustomCheck())
    report = KnowledgeQualityCenter(registry).evaluate(
        {"macroareas": [], "areas": [], "subareas": []}
    )

    assert report.score == 75.0
    assert report.dimensions == (("personalizzata", 75.0),)
    assert report.checklist[0].label == "Controllo esterno"


def test_markdown_table_import_parser(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    content = """
# Ontologia

| id | type | label | description | parent |
| --- | --- | --- | --- | --- |
| md_root | macroarea | Radice Markdown | Importazione Markdown | null |
"""

    result = _import_preview(client, "ontology.md", content)

    assert result["format"] == "markdown"
    assert result["parser"] == "markdown-internal"
    assert result["nodes_found"] == 1
    assert result["importable"] is True


def test_docx_table_import_parser(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)
    cells = (
        ("id", "type", "label", "description", "parent"),
        ("docx_root", "macroarea", "Radice DOCX", "Importazione DOCX", "null"),
    )
    rows = "".join(
        "<w:tr>"
        + "".join(f"<w:tc><w:p><w:r><w:t>{value}</w:t></w:r></w:p></w:tc>" for value in row)
        + "</w:tr>"
        for row in cells
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body><w:tbl>{rows}</w:tbl></w:body></w:document>"
    )
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("word/document.xml", document)

    result = _import_preview(client, "ontology.docx", stream.getvalue())

    assert result["format"] == "docx"
    assert result["parser"] == "docx-internal"
    assert result["nodes_found"] == 1
    assert result["importable"] is True
