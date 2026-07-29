"""Deterministic advisory heuristics for semantic graph review."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from ikg.graph import Entity, KnowledgeGraph

from .models import ReviewSeverity, ReviewSuggestion

EXPECTED_DEPTH = {"Macroarea": 0, "Area": 1, "Sottoarea": 2, "Concetto": 3}
SHORT_LABEL_LENGTH = 2
MANY_RELATIONSHIPS = 10


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _suggestion(
    category: str,
    entity_id: str,
    severity: ReviewSeverity,
    title: str,
    explanation: str,
    confidence: float,
) -> ReviewSuggestion:
    return ReviewSuggestion(
        id=f"review:{category}:{entity_id}",
        severity=severity,
        category=category,
        entity_id=entity_id,
        title=title,
        explanation=explanation,
        confidence=confidence,
    )


def _leading_case(label: str) -> bool | None:
    for character in label:
        if character.isalpha():
            return character.isupper()
    return None


def _hierarchy_depth(entity: Entity, entities: dict[str, Entity]) -> int | None:
    depth = 0
    current = entity
    visited: set[str] = set()
    while current.entity_type != "Macroarea":
        if (
            not _non_empty_string(current.identifier)
            or current.identifier in visited
            or not _non_empty_string(current.parent)
        ):
            return None
        visited.add(current.identifier)
        parent = entities.get(current.parent)
        if parent is None:
            return None
        current = parent
        depth += 1
    return depth


@dataclass(frozen=True, slots=True)
class HeuristicReviewerProvider:
    """Produce deterministic, non-authoritative review suggestions."""

    def review(self, graph: KnowledgeGraph) -> tuple[ReviewSuggestion, ...]:
        entities = tuple(
            sorted(
                (
                    entity
                    for entity in graph.entities
                    if _non_empty_string(entity.identifier) and _non_empty_string(entity.label)
                ),
                key=lambda entity: entity.identifier,
            )
        )
        suggestions: list[ReviewSuggestion] = []
        suggestions.extend(self._short_labels(entities))
        suggestions.extend(self._duplicate_labels(entities))
        suggestions.extend(self._hierarchy_depths(entities))
        suggestions.extend(self._isolated_concepts(entities, graph))
        suggestions.extend(self._relationship_counts(entities, graph))
        suggestions.extend(self._naming_style(entities))
        return tuple(suggestions)

    def _short_labels(self, entities: tuple[Entity, ...]) -> tuple[ReviewSuggestion, ...]:
        return tuple(
            _suggestion(
                "short_label",
                entity.identifier,
                ReviewSeverity.LOW,
                "Label is unusually short",
                f"The label {entity.label!r} contains at most {SHORT_LABEL_LENGTH} characters.",
                0.85,
            )
            for entity in entities
            if len(entity.label.strip()) <= SHORT_LABEL_LENGTH
        )

    def _duplicate_labels(self, entities: tuple[Entity, ...]) -> tuple[ReviewSuggestion, ...]:
        groups: dict[str, list[str]] = {}
        for entity in entities:
            normalized = " ".join(entity.label.casefold().split())
            groups.setdefault(normalized, []).append(entity.identifier)

        suggestions: list[ReviewSuggestion] = []
        for identifiers in groups.values():
            if len(identifiers) < 2:
                continue
            for entity_id in identifiers:
                others = ", ".join(
                    identifier for identifier in identifiers if identifier != entity_id
                )
                suggestions.append(
                    _suggestion(
                        "duplicate_label",
                        entity_id,
                        ReviewSeverity.MEDIUM,
                        "Duplicate label detected",
                        f"The same normalized label is used by: {others}.",
                        0.95,
                    )
                )
        return tuple(suggestions)

    def _hierarchy_depths(self, entities: tuple[Entity, ...]) -> tuple[ReviewSuggestion, ...]:
        by_id = {entity.identifier: entity for entity in entities}
        suggestions: list[ReviewSuggestion] = []
        for entity in entities:
            expected = EXPECTED_DEPTH.get(entity.entity_type)
            depth = _hierarchy_depth(entity, by_id)
            if expected is None or depth is None or depth == expected:
                continue
            suggestions.append(
                _suggestion(
                    "hierarchy_depth",
                    entity.identifier,
                    ReviewSeverity.MEDIUM,
                    "Hierarchy depth looks unusual",
                    f"Expected depth {expected}, observed depth {depth}.",
                    0.9,
                )
            )
        return tuple(suggestions)

    def _isolated_concepts(
        self, entities: tuple[Entity, ...], graph: KnowledgeGraph
    ) -> tuple[ReviewSuggestion, ...]:
        connected: set[str] = set()
        for relationship in graph.relationships:
            if _non_empty_string(relationship.source):
                connected.add(relationship.source)
            if _non_empty_string(relationship.target):
                connected.add(relationship.target)
        return tuple(
            _suggestion(
                "isolated_concept",
                entity.identifier,
                ReviewSeverity.MEDIUM,
                "Concept has no relationships",
                "The concept is not connected by any canonical Relationship.",
                0.9,
            )
            for entity in entities
            if entity.entity_type == "Concetto" and entity.identifier not in connected
        )

    def _relationship_counts(
        self, entities: tuple[Entity, ...], graph: KnowledgeGraph
    ) -> tuple[ReviewSuggestion, ...]:
        counts: Counter[str] = Counter()
        for relationship in graph.relationships:
            if _non_empty_string(relationship.source):
                counts[relationship.source] += 1
            if (
                _non_empty_string(relationship.target)
                and relationship.target != relationship.source
            ):
                counts[relationship.target] += 1
        return tuple(
            _suggestion(
                "many_relationships",
                entity.identifier,
                ReviewSeverity.LOW,
                "Entity has unusually many relationships",
                f"The entity participates in {counts[entity.identifier]} relationships.",
                0.75,
            )
            for entity in entities
            if counts[entity.identifier] > MANY_RELATIONSHIPS
        )

    def _naming_style(self, entities: tuple[Entity, ...]) -> tuple[ReviewSuggestion, ...]:
        styles = {
            entity.identifier: _leading_case(entity.label)
            for entity in entities
            if _leading_case(entity.label) is not None
        }
        counts = Counter(styles.values())
        if counts[True] == counts[False]:
            return ()
        expected = counts[True] > counts[False]
        return tuple(
            _suggestion(
                "naming_style",
                entity.identifier,
                ReviewSeverity.LOW,
                "Label naming style is inconsistent",
                "The label capitalization differs from the dominant graph style.",
                0.7,
            )
            for entity in entities
            if styles.get(entity.identifier) is not None
            and styles[entity.identifier] is not expected
        )
