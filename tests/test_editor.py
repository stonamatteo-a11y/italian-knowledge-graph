from __future__ import annotations

import json
import runpy
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from editor import create_app
from scripts.generate_seed import ONTOLOGY_DIR

CANONICAL_FILES = ("macroareas.json", "areas.json", "subareas.json")


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


def test_tree_loading(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    response = client.get("/api/tree")

    assert response.status_code == 200
    tree = response.json()
    assert len(tree) == 48
    assert len(_flatten_tree(tree)) == 1229
    assert tree[0]["id"] == "lingua_italiana"
    assert tree[0]["children"]


def test_node_api_exposes_editor_metadata(tmp_path: Path) -> None:
    client, _ = _editor_client(tmp_path)

    response = client.get("/api/node/mat_algebra")

    assert response.status_code == 200
    node = response.json()
    assert node["type"] == "area"
    assert node["parent_id"] == "matematica"
    assert node["children_count"] > 0
    assert [item["id"] for item in node["path"]] == ["matematica", "mat_algebra"]


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

    payload["label"] = "Test aggiornato"
    updated = client.put("/api/node/test_macroarea", json=payload)
    assert updated.status_code == 200
    assert updated.json()["label"] == "Test aggiornato"

    deleted = client.delete("/api/node/test_macroarea")
    assert deleted.status_code == 204
    assert client.get("/api/node/test_macroarea").status_code == 404


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
