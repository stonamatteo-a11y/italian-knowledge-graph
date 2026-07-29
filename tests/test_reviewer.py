from dataclasses import FrozenInstanceError

import pytest

from ikg.graph import Entity, KnowledgeGraph, Relationship
from ikg.reviewer import AIReviewer, ReviewReport, ReviewSeverity


def _hierarchy(*extra_entities: Entity) -> KnowledgeGraph:
    return KnowledgeGraph(
        entities=(
            Entity("m1", "Macroarea", "Scienze"),
            Entity("a1", "Area", "Fisica", "m1"),
            Entity("s1", "Sottoarea", "Meccanica", "a1"),
            *extra_entities,
        )
    )


def test_empty_graph_has_no_suggestions() -> None:
    report = AIReviewer().review(KnowledgeGraph(entities=()))

    assert report == ReviewReport(suggestions=())


def test_duplicated_labels_are_advisory_suggestions() -> None:
    graph = KnowledgeGraph(
        entities=(
            Entity("m1", "Macroarea", "Scienze"),
            Entity("m2", "Macroarea", " scienze "),
        )
    )

    report = AIReviewer().review(graph)
    duplicates = [
        suggestion for suggestion in report.suggestions if suggestion.category == "duplicate_label"
    ]

    assert [suggestion.entity_id for suggestion in duplicates] == ["m1", "m2"]
    assert all(suggestion.severity is ReviewSeverity.MEDIUM for suggestion in duplicates)


def test_isolated_concept_is_suggested() -> None:
    graph = _hierarchy(Entity("c1", "Concetto", "Forza", "s1"))

    report = AIReviewer().review(graph)

    assert any(
        suggestion.category == "isolated_concept" and suggestion.entity_id == "c1"
        for suggestion in report.suggestions
    )


def test_connected_concept_is_not_isolated() -> None:
    base = _hierarchy(Entity("c1", "Concetto", "Forza", "s1"))
    graph = KnowledgeGraph(
        entities=base.entities,
        relationships=(Relationship("r1", "CONTAINS", "s1", "c1"),),
    )

    report = AIReviewer().review(graph)

    assert not any(suggestion.category == "isolated_concept" for suggestion in report.suggestions)


def test_reviewer_output_is_deterministic_across_input_order_and_runs() -> None:
    graph = KnowledgeGraph(
        entities=(
            Entity("m2", "Macroarea", "A"),
            Entity("m1", "Macroarea", "A"),
        )
    )
    reordered = KnowledgeGraph(entities=tuple(reversed(graph.entities)))

    first = AIReviewer().review(graph)
    second = AIReviewer().review(graph)
    third = AIReviewer().review(reordered)

    assert first == second == third
    assert graph == KnowledgeGraph(
        entities=(
            Entity("m2", "Macroarea", "A"),
            Entity("m1", "Macroarea", "A"),
        )
    )


def test_report_orders_severity_then_entity_and_category() -> None:
    graph = _hierarchy(
        Entity("c2", "Concetto", "X", "s1"),
        Entity("c1", "Concetto", "Y", "s1"),
    )

    report = AIReviewer().review(graph)
    ordering = [
        (suggestion.severity, suggestion.entity_id, suggestion.category)
        for suggestion in report.suggestions
    ]

    assert ordering == [
        (ReviewSeverity.MEDIUM, "c1", "isolated_concept"),
        (ReviewSeverity.MEDIUM, "c2", "isolated_concept"),
        (ReviewSeverity.LOW, "c1", "short_label"),
        (ReviewSeverity.LOW, "c2", "short_label"),
    ]


def test_review_models_are_immutable() -> None:
    report = AIReviewer().review(_hierarchy(Entity("c1", "Concetto", "X", "s1")))

    with pytest.raises(FrozenInstanceError):
        report.suggestions = ()
