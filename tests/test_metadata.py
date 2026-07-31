from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from editor import create_app
from ikg.dataset import DatasetGenerator, JsonlExporter
from ikg.graph import Entity, KnowledgeGraph, load_graph
from ikg.metadata import MetadataError, canonical_metadata
from ikg.validator import ValidationEngine
from ikg.validator.builtin import core_rules
from scripts.generate_seed import (
    ONTOLOGY_DIR,
    SeedGenerationError,
    load_canonical,
    validate_canonical,
)


def _ontology_copy(tmp_path: Path) -> Path:
    target = tmp_path / "ontology"
    target.mkdir()
    for filename in ("macroareas.json", "areas.json", "subareas.json", "seed_compressed.py"):
        shutil.copyfile(ONTOLOGY_DIR / filename, target / filename)
    return target


def test_optional_metadata_defaults_to_empty_lists(tmp_path: Path) -> None:
    client = TestClient(create_app(_ontology_copy(tmp_path)))

    node = client.get("/api/node/mat_algebra").json()

    assert node["aliases"] == []
    assert node["sources"] == []
    assert node["notes"] == []
    assert node["relations"] == []


def test_metadata_normalization_is_deterministic() -> None:
    node = {
        "id": "n1",
        "label": "Algebra",
        "aliases": ["Calcolo simbolico", "calcolo simbolico", "Algebra astratta"],
        "sources": [
            {"title": "B", "url": "https://example.test/b"},
            {"url": "https://example.test/a", "title": "A"},
        ],
        "notes": ["Seconda", "Prima", "prima"],
        "relations": [],
    }

    first = canonical_metadata(node)
    second = canonical_metadata(node)

    assert first == second
    assert first["aliases"] == ["Algebra astratta", "Calcolo simbolico"]
    assert first["notes"] == ["Prima", "Seconda"]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("aliases", ["Algebra"], "primary label"),
        ("sources", [{}], "must not be empty"),
        ("sources", [{"url": "not a uri"}], "invalid source URL"),
        ("sources", [{"accessed_at": "31/07/2026"}], "accessed_at"),
        ("notes", [""], "non-empty strings"),
        ("relations", [{"predicate": "UNKNOWN", "target_id": "n2"}], "unknown relation"),
        ("relations", [{"predicate": "CONTAINS", "target_id": "n1"}], "self relation"),
    ],
)
def test_invalid_metadata_is_rejected(field: str, value: object, message: str) -> None:
    node = {"id": "n1", "label": "Algebra", field: value}

    with pytest.raises(MetadataError, match=message):
        canonical_metadata(node, {"n1", "n2"})


def test_editor_metadata_round_trip_survives_restart(tmp_path: Path) -> None:
    ontology_dir = _ontology_copy(tmp_path)
    client = TestClient(create_app(ontology_dir))
    node = client.get("/api/node/mat_algebra").json()
    payload = {
        field: node[field]
        for field in ("id", "type", "label", "description", "parent_id", "language")
    }
    payload.update(
        {
            "aliases": ["Algebra simbolica"],
            "sources": [
                {
                    "url": "https://example.test/algebra",
                    "title": "Algebra",
                    "publisher": "IKG",
                    "accessed_at": "2026-07-31",
                    "note": "Fonte di prova",
                }
            ],
            "notes": ["Nota persistente"],
            "relations": [],
        }
    )

    assert client.put("/api/node/mat_algebra", json=payload).status_code == 200
    assert client.post("/api/save").json()["saved"] is True

    reopened = TestClient(create_app(ontology_dir)).get("/api/node/mat_algebra").json()
    assert reopened["aliases"] == ["Algebra simbolica"]
    assert reopened["sources"][0]["publisher"] == "IKG"
    assert reopened["notes"] == ["Nota persistente"]
    persisted = json.loads((ontology_dir / "areas.json").read_text(encoding="utf-8"))
    assert next(record for record in persisted if record["id"] == "mat_algebra")["aliases"] == [
        "Algebra simbolica"
    ]

    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "entities": [
                    {
                        "id": reopened["id"],
                        "type": "Area",
                        "label": reopened["label"],
                        "parent": reopened["parent_id"],
                        "description": reopened["description"],
                        "language": reopened["language"],
                        "aliases": reopened["aliases"],
                        "sources": reopened["sources"],
                        "notes": reopened["notes"],
                        "relations": reopened["relations"],
                    }
                ],
                "relationships": [],
            }
        ),
        encoding="utf-8",
    )
    export_path = tmp_path / "dataset.jsonl"
    JsonlExporter().export(DatasetGenerator(load_graph(graph_path)).generate(), export_path)
    exported = json.loads(export_path.read_text(encoding="utf-8"))
    assert exported["aliases"] == ["Algebra simbolica"]
    assert exported["sources"] == reopened["sources"]
    assert exported["notes"] == ["Nota persistente"]


def test_existing_canonical_records_need_no_migration() -> None:
    records = load_canonical()

    validate_canonical(records)


def test_invalid_source_in_canonical_json_is_rejected() -> None:
    records = load_canonical()
    records["macroareas"][0]["sources"] = [{}]

    with pytest.raises(SeedGenerationError, match="source must not be empty"):
        validate_canonical(records)


def test_registered_containment_relation_cannot_duplicate_hierarchy(tmp_path: Path) -> None:
    client = TestClient(create_app(_ontology_copy(tmp_path)))
    node = client.get("/api/node/mat_algebra").json()
    payload = {
        field: node[field]
        for field in ("id", "type", "label", "description", "parent_id", "language")
    }
    payload["relations"] = [{"predicate": "CONTAINS", "target_id": "mat_al_equazioni"}]

    assert client.put("/api/node/mat_algebra", json=payload).status_code == 200
    result = client.post("/api/save")

    assert result.status_code == 422
    assert "duplicate canonical CONTAINS relation" in "\n".join(result.json()["errors"])


def test_authoritative_validator_reports_invalid_metadata() -> None:
    graph = KnowledgeGraph(
        entities=(
            Entity(
                "m1",
                "Macroarea",
                "Matematica",
                aliases=["Matematica"],
                sources=[],
                notes=[],
                relations=[],
            ),
        )
    )

    report = ValidationEngine(core_rules()).validate(graph)

    assert any(
        finding.rule_id == "IKG306" and "primary label" in finding.message
        for finding in report.findings
    )
