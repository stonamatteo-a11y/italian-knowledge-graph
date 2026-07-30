from __future__ import annotations

import json
import subprocess
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from editor import create_app
from editor.contribution.git import READ_ONLY_COMMANDS, GitInspector
from scripts.generate_seed import render_seed_module


def _records() -> dict[str, list[dict[str, str]]]:
    return {
        "macroareas": [
            {
                "id": "root_one",
                "label": "Radice uno",
                "description": "Descrizione completa della prima radice",
                "language": "it",
            },
            {
                "id": "root_two",
                "label": "Radice due",
                "description": "Descrizione completa della seconda radice",
                "language": "it",
            },
        ],
        "areas": [
            {
                "id": "area_one",
                "label": "Area uno",
                "parent_id": "root_one",
                "description": "Descrizione completa della prima area",
                "language": "it",
            },
            {
                "id": "area_two",
                "label": "Area due",
                "parent_id": "root_two",
                "description": "Descrizione completa della seconda area",
                "language": "it",
            },
        ],
        "subareas": [
            {
                "id": "leaf_one",
                "label": "Foglia uno",
                "parent_id": "area_one",
                "description": "Descrizione completa della prima foglia",
                "language": "it",
            },
            {
                "id": "leaf_two",
                "label": "Foglia due",
                "parent_id": "area_two",
                "description": "Descrizione completa della seconda foglia",
                "language": "it",
            },
        ],
    }


def _write_ontology(root: Path) -> Path:
    ontology_dir = root / "ontology"
    ontology_dir.mkdir()
    records = _records()
    for section, filename in (
        ("macroareas", "macroareas.json"),
        ("areas", "areas.json"),
        ("subareas", "subareas.json"),
    ):
        (ontology_dir / filename).write_text(
            json.dumps(records[section], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    (ontology_dir / "seed_compressed.py").write_text(
        render_seed_module(records),
        encoding="utf-8",
    )
    return ontology_dir


def _client(
    tmp_path: Path,
    *,
    git: bool = False,
    dirty_before_session: bool = False,
) -> tuple[TestClient, Path]:
    ontology_dir = _write_ontology(tmp_path)
    if git:
        subprocess.run(("git", "init", "-q"), cwd=tmp_path, check=True)
        subprocess.run(("git", "add", "ontology"), cwd=tmp_path, check=True)
        subprocess.run(
            (
                "git",
                "-c",
                "user.name=IKG Test",
                "-c",
                "user.email=ikg@example.invalid",
                "commit",
                "-qm",
                "initial ontology",
            ),
            cwd=tmp_path,
            check=True,
        )
        if dirty_before_session:
            (tmp_path / "unrelated.txt").write_text("unrelated", encoding="utf-8")
    return TestClient(create_app(ontology_dir)), ontology_dir


def _node_payload(client: TestClient, node_id: str) -> dict[str, object]:
    node = client.get(f"/api/node/{node_id}").json()
    return {
        field: node[field]
        for field in ("id", "type", "label", "description", "parent_id", "language")
    }


def test_contribution_detects_node_and_relationship_changes(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    assert client.get("/api/contribution/status").json() == {"changed": False}
    payload = _node_payload(client, "area_one")
    payload["label"] = "Area uno aggiornata"
    payload["parent_id"] = "root_two"

    assert client.put("/api/node/area_one", json=payload).status_code == 200
    assert client.get("/api/contribution/status").json() == {"changed": True}
    preview = client.get("/api/contribution/preview").json()

    assert preview["changed"] is True
    assert preview["changes"]["nodes"]["modified"] == ["area_one"]
    assert preview["changes"]["relationships"]["modified"] == [
        {"target": "area_one", "before": "root_one", "after": "root_two"}
    ]
    assert preview["changes"]["relationships"]["added"] == []
    assert preview["changes"]["relationships"]["removed"] == []
    assert preview["files"] == ["ontology/areas.json", "ontology/seed_compressed.py"]
    assert "Area uno aggiornata" in preview["diff"]


def test_contribution_detects_added_removed_and_excluded_content(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    created = {
        "id": "leaf_new",
        "type": "sottoarea",
        "label": "Foglia nuova",
        "description": "Descrizione completa della nuova foglia",
        "parent_id": "area_one",
        "language": "it",
    }

    assert client.post("/api/node", json=created).status_code == 201
    assert client.delete("/api/node/leaf_two").status_code == 204
    preview = client.get("/api/contribution/preview").json()

    assert preview["changes"]["nodes"]["added"] == ["leaf_new"]
    assert preview["changes"]["nodes"]["removed"] == ["leaf_two"]
    assert preview["changes"]["relationships"]["added"] == [
        {"source": "area_one", "target": "leaf_new"}
    ]
    assert preview["changes"]["relationships"]["removed"] == [
        {"source": "area_two", "target": "leaf_two"}
    ]
    assert preview["excluded"] == ["leaf_two"]


def test_contribution_zip_is_reproducible_and_contains_only_review_data(
    tmp_path: Path,
) -> None:
    client, _ = _client(tmp_path)
    payload = _node_payload(client, "leaf_one")
    payload["label"] = "Foglia uno aggiornata"
    assert client.put("/api/node/leaf_one", json=payload).status_code == 200

    first = client.post(
        "/api/contribution/package",
        json={"filename": "first.zip", "accepted_warning_ids": []},
    )
    second = client.post(
        "/api/contribution/package",
        json={"filename": "second.zip", "accepted_warning_ids": []},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    first_path = tmp_path / first.json()["output"]
    second_path = tmp_path / second.json()["output"]
    assert first_path.read_bytes() == second_path.read_bytes()
    with zipfile.ZipFile(first_path) as archive:
        names = archive.namelist()
        assert names == sorted(names)
        assert {
            "contribution.json",
            "validation-report.json",
            "quality-report.json",
            "CHANGELOG.md",
            "README.txt",
            "ontology/subareas.json",
        }.issubset(names)
        assert not any(name.endswith((".py", ".exe", ".bat", ".ps1")) for name in names)
        assert not any(name.startswith("/") or ".." in Path(name).parts for name in names)


def test_contribution_blocks_validation_errors(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    payload = _node_payload(client, "area_one")
    payload["parent_id"] = "missing_parent"
    assert client.put("/api/node/area_one", json=payload).status_code == 200

    preview = client.get("/api/contribution/preview").json()
    prepared = client.post(
        "/api/contribution/package",
        json={"filename": "invalid.zip", "accepted_warning_ids": []},
    )

    assert preview["errors"]
    assert preview["preparable"] is False
    assert prepared.status_code == 409
    assert not (tmp_path / "contributions" / "invalid.zip").exists()


def test_contribution_requires_explicit_warning_acceptance(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    payload = _node_payload(client, "leaf_one")
    payload["description"] = "Breve"
    assert client.put("/api/node/leaf_one", json=payload).status_code == 200
    preview = client.get("/api/contribution/preview").json()
    warning_ids = [warning["id"] for warning in preview["warnings"]]

    rejected = client.post(
        "/api/contribution/package",
        json={"filename": "warning.zip", "accepted_warning_ids": []},
    )
    accepted = client.post(
        "/api/contribution/package",
        json={"filename": "warning.zip", "accepted_warning_ids": warning_ids},
    )

    assert warning_ids
    assert rejected.status_code == 409
    assert accepted.status_code == 200
    assert accepted.json()["warnings_accepted"] == preview["warnings"]


def test_contribution_rejects_path_traversal(tmp_path: Path) -> None:
    client, _ = _client(tmp_path)
    payload = _node_payload(client, "leaf_one")
    payload["label"] = "Foglia modificata"
    assert client.put("/api/node/leaf_one", json=payload).status_code == 200

    response = client.post(
        "/api/contribution/package",
        json={"filename": "../outside.zip", "accepted_warning_ids": []},
    )

    assert response.status_code == 409
    assert not (tmp_path.parent / "outside.zip").exists()


def test_git_preparation_blocks_preexisting_worktree_changes(tmp_path: Path) -> None:
    client, _ = _client(tmp_path, git=True, dirty_before_session=True)
    payload = _node_payload(client, "leaf_one")
    payload["label"] = "Foglia modificata"
    assert client.put("/api/node/leaf_one", json=payload).status_code == 200

    preview = client.get("/api/contribution/preview").json()
    before = subprocess.check_output(("git", "rev-list", "--count", "HEAD"), cwd=tmp_path)
    response = client.post(
        "/api/contribution/git",
        json={"accepted_warning_ids": []},
    )
    after = subprocess.check_output(("git", "rev-list", "--count", "HEAD"), cwd=tmp_path)

    assert preview["git"]["available"] is True
    assert preview["git"]["blockers"] == ["unrelated.txt"]
    assert response.status_code == 409
    assert before == after


def test_git_preparation_writes_files_without_committing(tmp_path: Path) -> None:
    client, _ = _client(tmp_path, git=True)
    payload = _node_payload(client, "leaf_one")
    payload["label"] = "Foglia preparata per Git"
    assert client.put("/api/node/leaf_one", json=payload).status_code == 200
    before = subprocess.check_output(("git", "rev-list", "--count", "HEAD"), cwd=tmp_path)

    response = client.post(
        "/api/contribution/git",
        json={"accepted_warning_ids": []},
    )

    after = subprocess.check_output(("git", "rev-list", "--count", "HEAD"), cwd=tmp_path)
    changed_files = subprocess.check_output(
        ("git", "diff", "--name-only", "HEAD"),
        cwd=tmp_path,
        text=True,
    ).splitlines()
    assert response.status_code == 200
    assert response.json()["mode"] == "git"
    assert response.json()["output"] == [
        "ontology/subareas.json",
        "ontology/seed_compressed.py",
    ]
    assert before == after
    assert changed_files == [
        "ontology/seed_compressed.py",
        "ontology/subareas.json",
    ]


def test_git_preparation_does_not_overwrite_external_canonical_change(
    tmp_path: Path,
) -> None:
    client, ontology_dir = _client(tmp_path, git=True)
    payload = _node_payload(client, "leaf_one")
    payload["label"] = "Modifica della sessione"
    assert client.put("/api/node/leaf_one", json=payload).status_code == 200
    external_content = '{"external": "unrelated"}\n'
    (ontology_dir / "subareas.json").write_text(external_content, encoding="utf-8")

    preview = client.get("/api/contribution/preview").json()
    response = client.post(
        "/api/contribution/git",
        json={"accepted_warning_ids": []},
    )

    assert "ontology/subareas.json" in preview["git"]["blockers"]
    assert response.status_code == 409
    assert (ontology_dir / "subareas.json").read_text(encoding="utf-8") == external_content


def test_git_inspector_allows_only_read_only_commands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_run(arguments: tuple[str, ...], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(arguments)
        output = "true\n" if arguments[1] == "rev-parse" else ""
        return subprocess.CompletedProcess(arguments, 0, output, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    inspector = GitInspector(tmp_path)

    state = inspector.inspect()

    assert state.available is True
    assert all(tuple(arguments[1:]) in READ_ONLY_COMMANDS for arguments in calls)
    with pytest.raises(ValueError):
        inspector._run(("commit", "-m", "forbidden"))
