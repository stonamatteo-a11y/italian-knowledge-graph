from __future__ import annotations

import io
import json
import shutil
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from editor import create_app
from scripts.generate_seed import ONTOLOGY_DIR

CANONICAL_FILES = ("macroareas.json", "areas.json", "subareas.json")


def _client(tmp_path: Path) -> tuple[TestClient, Path]:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir()
    for filename in (*CANONICAL_FILES, "seed_compressed.py"):
        shutil.copyfile(ONTOLOGY_DIR / filename, ontology_dir / filename)
    return TestClient(create_app(ontology_dir)), ontology_dir


def _request() -> dict[str, object]:
    return {
        "domain_id": "matematica",
        "area_id": "mat_algebra",
        "subarea_id": None,
        "node_id": None,
        "fields": ["description", "source", "new_concepts"],
        "filename": "guided.zip",
    }


def test_guided_package_contains_docx_readme_and_metadata(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)

    preview = client.post("/api/contribution/guided/preview", json=_request())
    created = client.post("/api/contribution/guided/package", json=_request())

    assert preview.status_code == 200
    assert preview.json()["domain"] == "Matematica"
    assert preview.json()["area"] == "Algebra"
    assert created.status_code == 200
    package = Path(created.json()["path"])
    with zipfile.ZipFile(package) as archive:
        assert archive.namelist() == ["contribution.docx", "README.txt", "metadata.json"]
        metadata = json.loads(archive.read("metadata.json"))
        assert metadata["domain"] == "Matematica"
        assert metadata["area"] == "Algebra"
        assert metadata["node_count"] == preview.json()["nodes"]
        assert metadata["import_file"] == "contribution.docx"
        assert b"Importa Ontologia" in archive.read("README.txt")
        with zipfile.ZipFile(io.BytesIO(archive.read("contribution.docx"))) as document:
            xml = document.read("word/document.xml")
            assert b"Italian Knowledge Graph" in xml
            assert b"Nuovi concetti" in xml


def test_guided_package_is_deterministic_and_docx_is_importable(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)

    first = client.post("/api/contribution/guided/package", json=_request()).json()
    first_bytes = Path(first["path"]).read_bytes()
    second = client.post("/api/contribution/guided/package", json=_request()).json()
    second_bytes = Path(second["path"]).read_bytes()

    assert first_bytes == second_bytes
    with zipfile.ZipFile(io.BytesIO(first_bytes)) as archive:
        docx = archive.read("contribution.docx")
    imported = client.post(
        "/api/import/preview",
        params={"filename": "contribution.docx"},
        content=docx,
        headers={"Content-Type": "application/octet-stream"},
    )
    assert imported.status_code == 200
    assert imported.json()["format"] == "docx"
    assert imported.json()["importable"] is True


def test_docx_import_allows_description_completion_but_protects_identity(
    tmp_path: Path,
) -> None:
    client, _ = _client(tmp_path)
    client.post("/api/contribution/guided/package", json=_request())
    package = tmp_path / "contributions" / "guided.zip"
    with zipfile.ZipFile(package) as archive:
        docx = archive.read("contribution.docx")
    source = io.BytesIO(docx)
    output = io.BytesIO()
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(output, "w") as changed:
        for info in original.infolist():
            content = original.read(info.filename)
            if info.filename == "word/document.xml":
                content = content.replace(
                    b"Strutture, operazioni e relazioni algebriche",
                    b"Descrizione completata dal contributore",
                )
            changed.writestr(info, content)

    preview = client.post(
        "/api/import/preview",
        params={"filename": "contribution.docx"},
        content=output.getvalue(),
        headers={"Content-Type": "application/octet-stream"},
    )

    assert preview.status_code == 200
    assert preview.json()["importable"] is True
    assert preview.json()["collisions"] == []


def test_docx_import_reads_new_concepts_table(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    client.post("/api/contribution/guided/package", json=_request())
    package = tmp_path / "contributions" / "guided.zip"
    with zipfile.ZipFile(package) as archive:
        docx = archive.read("contribution.docx")
    source = io.BytesIO(docx)
    output = io.BytesIO()
    values = (
        "guided_new_area",
        "area",
        "matematica",
        "Nuova area guidata",
        "Descrizione del nuovo nodo",
        "",
        "",
        "",
    )
    row = (
        "<w:tr>"
        + "".join(f"<w:tc><w:p><w:r><w:t>{value}</w:t></w:r></w:p></w:tc>" for value in values)
        + "</w:tr>"
    ).encode()
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(output, "w") as changed:
        for info in original.infolist():
            content = original.read(info.filename)
            if info.filename == "word/document.xml":
                head, tail = content.rsplit(b"</w:tbl>", 1)
                content = head + row + b"</w:tbl>" + tail
            changed.writestr(info, content)

    preview = client.post(
        "/api/import/preview",
        params={"filename": "contribution.docx"},
        content=output.getvalue(),
        headers={"Content-Type": "application/octet-stream"},
    )

    assert preview.status_code == 200
    assert preview.json()["importable"] is True
    assert preview.json()["nodes_to_add"] == 1


def test_guided_package_rejects_path_traversal(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    payload = {**_request(), "filename": "../outside.zip"}

    response = client.post("/api/contribution/guided/package", json=payload)

    assert response.status_code == 422
    assert not (tmp_path / "outside.zip").exists()
