from ikg.graph import Entity, KnowledgeGraph
from ikg.validator import ValidationEngine
from ikg.validator.builtin import core_rules


def test_valid_hierarchy_passes_core_rules() -> None:
    graph = KnowledgeGraph(
        entities=(
            Entity("m1", "Macroarea", "Scienze"),
            Entity("a1", "Area", "Fisica", "m1"),
            Entity("s1", "Sottoarea", "Meccanica", "a1"),
            Entity("c1", "Concetto", "Forza", "s1"),
        )
    )

    report = ValidationEngine(core_rules()).validate(graph)

    assert report.is_valid is True
    assert report.findings == ()


def test_core_rules_detect_structural_failures() -> None:
    graph = KnowledgeGraph(
        entities=(
            Entity("m1", "Macroarea", "Scienze"),
            Entity("dup", "Area", "Fisica", "missing"),
            Entity("dup", "WrongType", "Duplicato", "dup"),
            Entity("c1", "Concetto", "Senza parent"),
        )
    )

    report = ValidationEngine(core_rules()).validate(graph)
    rule_ids = {finding.rule_id for finding in report.findings}

    assert report.is_valid is False
    assert {"IKG004", "IKG100", "IKG200", "IKG203", "IKG204"} <= rule_ids
