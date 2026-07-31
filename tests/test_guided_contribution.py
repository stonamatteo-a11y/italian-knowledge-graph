from __future__ import annotations

import io
import json
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import pytest
from fastapi.testclient import TestClient

from editor import create_app
from scripts.generate_seed import ONTOLOGY_DIR

CANONICAL_FILES = ("macroareas.json", "areas.json", "subareas.json")
WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": WORD_NAMESPACE}


def _client(tmp_path: Path) -> tuple[TestClient, Path]:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir()
    for filename in (*CANONICAL_FILES, "seed_compressed.py"):
        shutil.copyfile(ONTOLOGY_DIR / filename, ontology_dir / filename)
    return TestClient(create_app(ontology_dir)), ontology_dir


def _request(**overrides: object) -> dict[str, object]:
    return {
        "domain_id": "matematica",
        "area_id": "mat_algebra",
        "subarea_id": None,
        "node_id": None,
        "fields": ["description", "source", "new_concepts"],
        "node_limit": "10",
        "filename": "guided.zip",
        **overrides,
    }


def _package_docx(package: Path) -> bytes:
    with zipfile.ZipFile(package) as archive:
        return archive.read("contribution.docx")


def _replace_docx_document(docx: bytes, document: bytes) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(docx)) as original, zipfile.ZipFile(output, "w") as changed:
        for info in original.infolist():
            changed.writestr(
                info,
                document if info.filename == "word/document.xml" else original.read(info.filename),
            )
    return output.getvalue()


def _edit_card(
    docx: bytes,
    marker: str,
    replacements: dict[str, str],
    *,
    card_index: int = 0,
) -> bytes:
    with zipfile.ZipFile(io.BytesIO(docx)) as archive:
        document = archive.read("word/document.xml")
    root = ElementTree.fromstring(document)
    cards = []
    for table in root.findall(".//w:tbl", NS):
        text = "".join(table.itertext())
        if marker in text:
            cards.append(table)
    table = cards[card_index]
    for row in table.findall("./w:tr", NS):
        cells = row.findall("./w:tc", NS)
        if len(cells) < 2:
            continue
        label = "".join(cells[0].itertext())
        label = label.removesuffix("Protetto").removesuffix("Da compilare")
        if label not in replacements:
            continue
        text = cells[1].find(".//w:t", NS)
        assert text is not None
        text.text = replacements[label]
    return _replace_docx_document(
        docx,
        ElementTree.tostring(root, encoding="utf-8", xml_declaration=True),
    )


def _import_preview(client: TestClient, docx: bytes) -> dict[str, object]:
    response = client.post(
        "/api/import/preview",
        params={"filename": "contribution.docx"},
        content=docx,
        headers={"Content-Type": "application/octet-stream"},
    )
    assert response.status_code == 200
    return response.json()


def test_guided_package_contains_vertical_docx_readme_and_metadata(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)

    preview = client.post("/api/contribution/guided/preview", json=_request()).json()
    created = client.post("/api/contribution/guided/package", json=_request()).json()
    package = Path(created["path"])

    with zipfile.ZipFile(package) as archive:
        assert archive.namelist() == ["contribution.docx", "README.txt", "metadata.json"]
        metadata = json.loads(archive.read("metadata.json"))
        assert metadata["template_version"] == "2"
        assert metadata["layout_version"] == "2"
        assert metadata["selected_domain"] == "matematica"
        assert metadata["selected_area"] == "mat_algebra"
        assert metadata["requested_node_limit"] == "10"
        assert metadata["included_node_ids"] == preview["included_node_ids"]
        assert len(metadata["canonical_snapshot"]) == 64
        assert metadata["contribution_id"].startswith("ikg-")
        readme = archive.read("README.txt").decode()
        assert "Apri contribution.docx" in readme
        assert "Preview, revisione e Validator" in readme
        with zipfile.ZipFile(io.BytesIO(archive.read("contribution.docx"))) as document:
            xml = document.read("word/document.xml")
            assert b"Richiesta di contributo" in xml
            assert b"Abbiamo bisogno della tua competenza" in xml
            assert b"IKG_NODE_CARD_V2" in xml
            assert b"IKG_NEW_NODE_CARD_V2" in xml
            assert b"Protetto" in xml
            assert b"Da compilare" in xml
            assert b"w:cantSplit" in xml
            assert b'<w:pgSz w:w="11906" w:h="16838"' in xml
            assert b"<w:tblGrid>" not in xml


@pytest.mark.parametrize(
    ("node_limit", "expected"),
    (("selected", 1), ("10", 10), ("25", 25), ("50", 50)),
)
def test_guided_preview_applies_node_limits(
    tmp_path: Path,
    node_limit: str,
    expected: int,
) -> None:
    client, _ = _client(tmp_path)

    preview = client.post(
        "/api/contribution/guided/preview",
        json=_request(area_id=None, node_limit=node_limit),
    ).json()

    assert preview["included_nodes"] == expected
    assert preview["total_nodes"] > expected
    assert preview["excluded_nodes"] == preview["total_nodes"] - expected


def test_guided_preview_can_include_the_whole_ordered_branch(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)

    preview = client.post(
        "/api/contribution/guided/preview",
        json=_request(area_id=None, node_limit="all"),
    ).json()

    assert preview["included_nodes"] == preview["total_nodes"]
    assert preview["excluded_nodes"] == 0
    assert preview["included_node_ids"][0] == "matematica"
    assert preview["included_node_ids"][1:4] == [
        "mat_algebra",
        "mat_al_equazioni",
        "mat_al_matrici",
    ]


def test_guided_package_is_deterministic_and_empty_cards_are_ignored(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)

    first = client.post("/api/contribution/guided/package", json=_request()).json()
    first_bytes = Path(first["path"]).read_bytes()
    second = client.post("/api/contribution/guided/package", json=_request()).json()
    second_bytes = Path(second["path"]).read_bytes()

    assert first_bytes == second_bytes
    imported = _import_preview(client, _package_docx(Path(first["path"])))
    assert imported["format"] == "docx"
    assert imported["importable"] is True
    assert imported["nodes_found"] == first["included_nodes"]


def test_docx_import_applies_proposed_description(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    created = client.post("/api/contribution/guided/package", json=_request()).json()
    docx = _edit_card(
        _package_docx(Path(created["path"])),
        "IKG_NODE_CARD_V2",
        {"Nuova descrizione o proposta di correzione": ("Descrizione completata dal contributore")},
    )

    preview = _import_preview(client, docx)

    assert preview["importable"] is True
    assert preview["collisions"] == []
    assert any(
        "proposed description: Descrizione completata dal contributore" in modification
        for modification in preview["modifications"]
    )
    confirmed = client.post(
        "/api/import/confirm",
        json={"token": preview["token"], "accepted_warnings": []},
    )
    assert confirmed.status_code == 200
    assert (
        client.get("/api/node/mat_algebra").json()["description"]
        == "Descrizione completata dal contributore"
    )


def test_docx_import_preserves_canonical_metadata(tmp_path: Path) -> None:
    client, ontology_dir = _client(tmp_path)
    created = client.post("/api/contribution/guided/package", json=_request()).json()
    docx = _edit_card(
        _package_docx(Path(created["path"])),
        "IKG_NODE_CARD_V2",
        {
            "Fonte": "Enciclopedia di riferimento",
            "Sinonimi": "algebra simbolica",
            "Note e osservazioni": "Verificare la terminologia",
        },
    )

    preview = _import_preview(client, docx)

    assert preview["importable"] is True
    confirmed = client.post(
        "/api/import/confirm",
        json={"token": preview["token"], "accepted_warnings": []},
    )
    assert confirmed.status_code == 200
    node = client.get("/api/node/mat_algebra").json()
    assert node["aliases"] == ["algebra simbolica"]
    assert node["sources"] == [{"note": "Enciclopedia di riferimento"}]
    assert node["notes"] == ["Verificare la terminologia"]
    persisted = json.loads((ontology_dir / "areas.json").read_text(encoding="utf-8"))
    assert next(item for item in persisted if item["id"] == "mat_algebra")["sources"] == [
        {"note": "Enciclopedia di riferimento"}
    ]


def test_docx_import_blocks_ambiguous_relationship_proposal(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    created = client.post("/api/contribution/guided/package", json=_request()).json()
    docx = _edit_card(
        _package_docx(Path(created["path"])),
        "IKG_NODE_CARD_V2",
        {"Nuove relazioni proposte": "RELATED_TO mat_geometria"},
    )

    preview = _import_preview(client, docx)

    assert preview["importable"] is False
    assert any("relations must contain objects" in error for error in preview["errors"])


def test_docx_import_preserves_multiple_structured_sources(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    created = client.post("/api/contribution/guided/package", json=_request()).json()
    docx = _edit_card(
        _package_docx(Path(created["path"])),
        "IKG_NODE_CARD_V2",
        {
            "Fonte": (
                "URL/URI: https://example.test/a\n"
                "Titolo: Fonte A\n\n"
                "URL/URI: urn:isbn:9780000000000\n"
                "Editore: Editore B\n"
                "Data di accesso: 2026-07-31"
            )
        },
    )

    preview = _import_preview(client, docx)

    assert preview["importable"] is True
    confirmed = client.post(
        "/api/import/confirm",
        json={"token": preview["token"], "accepted_warnings": []},
    )
    assert confirmed.status_code == 200
    assert client.get("/api/node/mat_algebra").json()["sources"] == [
        {
            "url": "urn:isbn:9780000000000",
            "publisher": "Editore B",
            "accessed_at": "2026-07-31",
        },
        {"title": "Fonte A", "url": "https://example.test/a"},
    ]


def test_docx_import_rejects_changes_to_protected_fields(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    created = client.post("/api/contribution/guided/package", json=_request()).json()
    docx = _edit_card(
        _package_docx(Path(created["path"])),
        "IKG_NODE_CARD_V2",
        {"Label": "Label modificata"},
    )

    preview = _import_preview(client, docx)

    assert preview["importable"] is False
    assert "mat_algebra" in preview["collisions"]
    assert any("conflicts with an existing canonical node" in error for error in preview["errors"])


def test_docx_import_reads_new_node_card(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    created = client.post("/api/contribution/guided/package", json=_request()).json()
    docx = _edit_card(
        _package_docx(Path(created["path"])),
        "IKG_NEW_NODE_CARD_V2",
        {
            "Parent proposto": "matematica",
            "ID proposto": "guided_new_area",
            "Tipo proposto": "area",
            "Label": "Nuova area guidata",
            "Descrizione": "Descrizione del nuovo nodo",
        },
    )

    preview = _import_preview(client, docx)

    assert preview["importable"] is True
    assert preview["nodes_to_add"] == 1


def test_guided_package_rejects_path_traversal(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    payload = _request(filename="../outside.zip")

    response = client.post("/api/contribution/guided/package", json=payload)

    assert response.status_code == 422
    assert not (tmp_path / "outside.zip").exists()
