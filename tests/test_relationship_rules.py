import json
from dataclasses import FrozenInstanceError

import pytest

from ikg.graph import Entity, KnowledgeGraph, Relationship, load_graph
from ikg.validator import ValidationEngine
from ikg.validator.builtin import core_rules


def _valid_entities() -> tuple[Entity, ...]:
    return (
        Entity("m1", "Macroarea", "Scienze"),
        Entity("a1", "Area", "Fisica", "m1"),
        Entity("s1", "Sottoarea", "Meccanica", "a1"),
        Entity("c1", "Concetto", "Forza", "s1"),
    )


def _report(*relationships: Relationship):
    graph = KnowledgeGraph(entities=_valid_entities(), relationships=relationships)
    return ValidationEngine(core_rules()).validate(graph)


def test_relationship_is_immutable() -> None:
    relationship = Relationship("r1", "CONTAINS", "m1", "a1")

    with pytest.raises(FrozenInstanceError):
        relationship.target = "s1"


def test_json_loader_supports_relationships_and_entity_only_documents(tmp_path) -> None:
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "entities": [{"id": "m1", "type": "Macroarea", "label": "Scienze"}],
                "relationships": [{"id": "r1", "type": "CONTAINS", "source": "m1", "target": "a1"}],
            }
        ),
        encoding="utf-8",
    )

    graph = load_graph(graph_path)
    assert graph.relationships == (Relationship("r1", "CONTAINS", "m1", "a1"),)

    graph_path.write_text(
        json.dumps({"entities": [{"id": "m1", "type": "Macroarea", "label": "Scienze"}]}),
        encoding="utf-8",
    )
    assert load_graph(graph_path).relationships == ()


def test_valid_graph_passes_relationship_rules() -> None:
    report = _report(
        Relationship("r1", "CONTAINS", "m1", "a1"),
        Relationship("r2", "CONTAINS", "a1", "s1"),
        Relationship("r3", "CONTAINS", "s1", "c1"),
    )

    assert report.is_valid is True
    assert report.findings == ()


@pytest.mark.parametrize(
    ("relationship", "rule_id"),
    (
        (Relationship("r1", "UNKNOWN", "m1", "a1"), "IKG300"),
        (Relationship("r1", "CONTAINS", "missing", "a1"), "IKG302"),
        (Relationship("r1", "CONTAINS", "m1", "missing"), "IKG301"),
        (Relationship("r1", "CONTAINS", "m1", "m1"), "IKG304"),
        (Relationship("r1", "CONTAINS", "a1", "m1"), "IKG305"),
    ),
)
def test_invalid_relationship_is_reported(relationship: Relationship, rule_id: str) -> None:
    assert rule_id in {finding.rule_id for finding in _report(relationship).findings}


def test_duplicate_relationship_is_reported_once_as_warning() -> None:
    report = _report(
        Relationship("r2", "CONTAINS", "m1", "a1"),
        Relationship("r1", "CONTAINS", "m1", "a1"),
    )

    findings = [finding for finding in report.findings if finding.rule_id == "IKG303"]
    assert len(findings) == 1
    assert findings[0].severity.value == "WARNING"
    assert report.is_valid is True


def test_relationship_findings_are_deterministic() -> None:
    relationships = (
        Relationship("z", "UNKNOWN", "m1", "a1"),
        Relationship("a", "UNKNOWN", "m1", "a1"),
    )

    first = _report(*relationships).findings
    second = _report(*reversed(relationships)).findings

    assert first == second
