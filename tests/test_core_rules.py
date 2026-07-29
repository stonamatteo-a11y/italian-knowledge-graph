from ikg.graph import Entity, KnowledgeGraph
from ikg.validator import ValidationEngine
from ikg.validator.builtin import DeprecatedIdentifierRule, core_rules


def _rule_ids(graph: KnowledgeGraph) -> set[str]:
    return {finding.rule_id for finding in ValidationEngine(core_rules()).validate(graph).findings}


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

    rule_ids = _rule_ids(graph)

    assert {"IKG004", "IKG100", "IKG200", "IKG203", "IKG204"} <= rule_ids


def test_schema_rules_detect_types_and_unknown_properties() -> None:
    graph = KnowledgeGraph(
        entities=(
            Entity(42, "Macroarea", ["invalid"], unknown_properties=("extra",)),
        )
    )

    assert {"IKG001", "IKG002", "IKG003"} <= _rule_ids(graph)


def test_identity_rules_detect_invalid_and_reserved_identifiers() -> None:
    graph = KnowledgeGraph(
        entities=(
            Entity("Bad Identifier", "Macroarea", "Invalid"),
            Entity("sys:internal", "Macroarea", "Reserved"),
        )
    )

    assert {"IKG101", "IKG102"} <= _rule_ids(graph)


def test_deprecated_identifier_rule_is_registry_driven() -> None:
    graph = KnowledgeGraph(entities=(Entity("old-id", "Macroarea", "Old"),))

    report = ValidationEngine((DeprecatedIdentifierRule(frozenset({"old-id"})),)).validate(graph)

    assert [finding.rule_id for finding in report.findings] == ["IKG103"]


def test_hierarchy_rules_detect_parent_type_multiplicity_and_level() -> None:
    graph = KnowledgeGraph(
        entities=(
            Entity("m1", "Macroarea", "Root"),
            Entity("m2", "Macroarea", "Root with parent", "m1"),
            Entity("s1", "Sottoarea", "Wrong parent", "m1"),
            Entity("c1", "Concetto", "Multiple", ["s1", "s2"]),
        )
    )

    assert {"IKG201", "IKG202", "IKG205"} <= _rule_ids(graph)
