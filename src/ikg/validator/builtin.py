"""Deterministic built-in validation rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ikg.graph import KnowledgeGraph

from .models import Finding, Severity

ALLOWED_TYPES = frozenset({"Macroarea", "Area", "Sottoarea", "Concetto"})
EXPECTED_PARENT_TYPE = {
    "Area": "Macroarea",
    "Sottoarea": "Area",
    "Concetto": "Sottoarea",
}
EXPECTED_DEPTH = {"Macroarea": 0, "Area": 1, "Sottoarea": 2, "Concetto": 3}
IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
RESERVED_IDENTIFIER_PREFIXES = ("__", "runtime:", "sys:")
RELATIONSHIP_TYPES = frozenset({"CONTAINS"})
RELATIONSHIP_DIRECTIONS = {
    "CONTAINS": frozenset(
        {
            ("Macroarea", "Area"),
            ("Area", "Sottoarea"),
            ("Sottoarea", "Concetto"),
        }
    )
}


def _location(index: int, identifier: Any) -> str:
    return identifier if isinstance(identifier, str) and identifier else f"entities[{index}]"


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _relationship_location(index: int, identifier: Any) -> str:
    return identifier if isinstance(identifier, str) and identifier else f"relationships[{index}]"


@dataclass(frozen=True, slots=True)
class MissingRequiredPropertyRule:
    rule_id: str = "IKG001"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        findings: list[Finding] = []
        for index, entity in enumerate(graph.entities):
            for name, value in (
                ("id", entity.identifier),
                ("type", entity.entity_type),
                ("label", entity.label),
            ):
                if not _non_empty_string(value):
                    findings.append(
                        Finding(
                            self.rule_id,
                            Severity.ERROR,
                            f"Missing required property: {name}",
                            f"entities[{index}]",
                        )
                    )
        for index, relationship in enumerate(graph.relationships):
            for name, value in (
                ("id", relationship.id),
                ("type", relationship.type),
                ("source", relationship.source),
                ("target", relationship.target),
            ):
                if not _non_empty_string(value):
                    findings.append(
                        Finding(
                            self.rule_id,
                            Severity.ERROR,
                            f"Missing required property: {name}",
                            f"relationships[{index}]",
                        )
                    )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class InvalidPropertyTypeRule:
    rule_id: str = "IKG002"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        findings: list[Finding] = []
        for index, entity in enumerate(graph.entities):
            location = _location(index, entity.identifier)
            for name, value in (
                ("id", entity.identifier),
                ("type", entity.entity_type),
                ("label", entity.label),
            ):
                if value is not None and not isinstance(value, str):
                    findings.append(
                        Finding(
                            self.rule_id,
                            Severity.ERROR,
                            f"Property {name!r} must be a string",
                            location,
                        )
                    )
            if entity.parent is not None and not isinstance(entity.parent, (str, list)):
                findings.append(
                    Finding(
                        self.rule_id,
                        Severity.ERROR,
                        "Property 'parent' must be a string or null",
                        location,
                    )
                )
        for index, relationship in enumerate(graph.relationships):
            location = _relationship_location(index, relationship.id)
            for name, value in (
                ("id", relationship.id),
                ("type", relationship.type),
                ("source", relationship.source),
                ("target", relationship.target),
            ):
                if value is not None and not isinstance(value, str):
                    findings.append(
                        Finding(
                            self.rule_id,
                            Severity.ERROR,
                            f"Property {name!r} must be a string",
                            location,
                        )
                    )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class UnknownPropertyRule:
    rule_id: str = "IKG003"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        entity_findings = tuple(
            Finding(
                self.rule_id,
                Severity.WARNING,
                f"Unknown property: {name}",
                _location(index, entity.identifier),
            )
            for index, entity in enumerate(graph.entities)
            for name in entity.unknown_properties
        )
        relationship_findings = tuple(
            Finding(
                self.rule_id,
                Severity.WARNING,
                f"Unknown property: {name}",
                _relationship_location(index, relationship.id),
            )
            for index, relationship in enumerate(graph.relationships)
            for name in relationship.unknown_properties
        )
        return entity_findings + relationship_findings


@dataclass(frozen=True, slots=True)
class InvalidEntityTypeRule:
    rule_id: str = "IKG004"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        return tuple(
            Finding(
                self.rule_id,
                Severity.ERROR,
                f"Invalid Entity type: {entity.entity_type!r}",
                _location(index, entity.identifier),
            )
            for index, entity in enumerate(graph.entities)
            if entity.entity_type not in ALLOWED_TYPES
        )


@dataclass(frozen=True, slots=True)
class DuplicateIdentifierRule:
    rule_id: str = "IKG100"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        counts: dict[str, int] = {}
        for entity in graph.entities:
            if _non_empty_string(entity.identifier):
                counts[entity.identifier] = counts.get(entity.identifier, 0) + 1
        return tuple(
            Finding(self.rule_id, Severity.ERROR, f"Duplicate identifier: {identifier}", identifier)
            for identifier, count in sorted(counts.items())
            if count > 1
        )


@dataclass(frozen=True, slots=True)
class InvalidIdentifierFormatRule:
    rule_id: str = "IKG101"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        return tuple(
            Finding(
                self.rule_id,
                Severity.ERROR,
                f"Invalid identifier format: {entity.identifier!r}",
                _location(index, entity.identifier),
            )
            for index, entity in enumerate(graph.entities)
            if _non_empty_string(entity.identifier)
            and IDENTIFIER_PATTERN.fullmatch(entity.identifier) is None
        )


@dataclass(frozen=True, slots=True)
class ReservedIdentifierRule:
    rule_id: str = "IKG102"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        return tuple(
            Finding(
                self.rule_id,
                Severity.ERROR,
                f"Reserved identifier: {entity.identifier}",
                entity.identifier,
            )
            for entity in graph.entities
            if _non_empty_string(entity.identifier)
            and entity.identifier.startswith(RESERVED_IDENTIFIER_PREFIXES)
        )


@dataclass(frozen=True, slots=True)
class DeprecatedIdentifierRule:
    deprecated_identifiers: frozenset[str] = field(default_factory=frozenset)
    rule_id: str = "IKG103"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        return tuple(
            Finding(
                self.rule_id,
                Severity.WARNING,
                f"Deprecated identifier: {entity.identifier}",
                entity.identifier,
            )
            for entity in graph.entities
            if isinstance(entity.identifier, str)
            and entity.identifier in self.deprecated_identifiers
        )


@dataclass(frozen=True, slots=True)
class MissingParentRule:
    rule_id: str = "IKG200"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        return tuple(
            Finding(
                self.rule_id,
                Severity.ERROR,
                "Non-root Entity has no parent",
                _location(index, entity.identifier),
            )
            for index, entity in enumerate(graph.entities)
            if entity.entity_type != "Macroarea" and (entity.parent is None or entity.parent == "")
        )


@dataclass(frozen=True, slots=True)
class InvalidParentTypeRule:
    rule_id: str = "IKG201"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        entities = {
            entity.identifier: entity
            for entity in graph.entities
            if _non_empty_string(entity.identifier)
        }
        findings: list[Finding] = []
        for index, entity in enumerate(graph.entities):
            expected = EXPECTED_PARENT_TYPE.get(entity.entity_type)
            if expected is None or not isinstance(entity.parent, str):
                continue
            parent = entities.get(entity.parent)
            if parent is not None and parent.entity_type != expected:
                findings.append(
                    Finding(
                        self.rule_id,
                        Severity.ERROR,
                        f"Expected parent type {expected}, found {parent.entity_type!r}",
                        _location(index, entity.identifier),
                    )
                )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class MultipleParentsRule:
    rule_id: str = "IKG202"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        return tuple(
            Finding(
                self.rule_id,
                Severity.ERROR,
                f"Entity has multiple parents: {len(entity.parent)}",
                _location(index, entity.identifier),
            )
            for index, entity in enumerate(graph.entities)
            if isinstance(entity.parent, list) and len(entity.parent) > 1
        )


@dataclass(frozen=True, slots=True)
class HierarchyCycleRule:
    rule_id: str = "IKG203"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        parents = {
            entity.identifier: entity.parent
            for entity in graph.entities
            if _non_empty_string(entity.identifier) and isinstance(entity.parent, str)
        }
        cyclic: set[str] = set()
        for start in sorted(parents):
            seen: set[str] = set()
            current: str | None = start
            while current is not None and current in parents:
                if current in seen:
                    cyclic.add(start)
                    break
                seen.add(current)
                current = parents[current]
        return tuple(
            Finding(self.rule_id, Severity.ERROR, "Hierarchy cycle detected", identifier)
            for identifier in sorted(cyclic)
        )


@dataclass(frozen=True, slots=True)
class OrphanEntityRule:
    rule_id: str = "IKG204"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        entities = {
            entity.identifier: entity
            for entity in graph.entities
            if _non_empty_string(entity.identifier)
        }
        orphans: list[str] = []
        for identifier, entity in sorted(entities.items()):
            if entity.entity_type == "Macroarea":
                continue
            visited: set[str] = set()
            current = entity
            while current.entity_type != "Macroarea":
                if (
                    current.identifier in visited
                    or not isinstance(current.parent, str)
                    or current.parent not in entities
                ):
                    orphans.append(identifier)
                    break
                visited.add(current.identifier)
                current = entities[current.parent]
        return tuple(
            Finding(
                self.rule_id,
                Severity.ERROR,
                "Entity is not reachable from a Macroarea",
                identifier,
            )
            for identifier in orphans
        )


@dataclass(frozen=True, slots=True)
class InvalidHierarchyLevelRule:
    rule_id: str = "IKG205"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        entities = {
            entity.identifier: entity
            for entity in graph.entities
            if _non_empty_string(entity.identifier)
        }
        findings: list[Finding] = []
        for index, entity in enumerate(graph.entities):
            expected_depth = EXPECTED_DEPTH.get(entity.entity_type)
            if expected_depth is None:
                continue
            if entity.entity_type == "Macroarea":
                if entity.parent is not None:
                    findings.append(
                        Finding(
                            self.rule_id,
                            Severity.ERROR,
                            "Macroarea must be a root Entity",
                            _location(index, entity.identifier),
                        )
                    )
                continue
            if not isinstance(entity.parent, str):
                continue
            depth = 0
            current = entity
            visited: set[str] = set()
            complete = True
            while current.entity_type != "Macroarea":
                if current.identifier in visited or not isinstance(current.parent, str):
                    complete = False
                    break
                visited.add(current.identifier)
                parent = entities.get(current.parent)
                if parent is None:
                    complete = False
                    break
                depth += 1
                current = parent
            if complete and depth != expected_depth:
                findings.append(
                    Finding(
                        self.rule_id,
                        Severity.ERROR,
                        f"Expected hierarchy depth {expected_depth}, found {depth}",
                        _location(index, entity.identifier),
                    )
                )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class UnknownRelationshipTypeRule:
    rule_id: str = "IKG300"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        return tuple(
            Finding(
                self.rule_id,
                Severity.ERROR,
                f"Unknown Relationship type: {relationship.type!r}",
                _relationship_location(index, relationship.id),
            )
            for index, relationship in enumerate(graph.relationships)
            if _non_empty_string(relationship.type) and relationship.type not in RELATIONSHIP_TYPES
        )


@dataclass(frozen=True, slots=True)
class MissingTargetEntityRule:
    rule_id: str = "IKG301"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        identifiers = {
            entity.identifier for entity in graph.entities if _non_empty_string(entity.identifier)
        }
        return tuple(
            Finding(
                self.rule_id,
                Severity.ERROR,
                f"Missing target Entity: {relationship.target!r}",
                _relationship_location(index, relationship.id),
            )
            for index, relationship in enumerate(graph.relationships)
            if _non_empty_string(relationship.target) and relationship.target not in identifiers
        )


@dataclass(frozen=True, slots=True)
class MissingSourceEntityRule:
    rule_id: str = "IKG302"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        identifiers = {
            entity.identifier for entity in graph.entities if _non_empty_string(entity.identifier)
        }
        return tuple(
            Finding(
                self.rule_id,
                Severity.ERROR,
                f"Missing source Entity: {relationship.source!r}",
                _relationship_location(index, relationship.id),
            )
            for index, relationship in enumerate(graph.relationships)
            if _non_empty_string(relationship.source) and relationship.source not in identifiers
        )


@dataclass(frozen=True, slots=True)
class DuplicateRelationshipRule:
    rule_id: str = "IKG303"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        counts: dict[tuple[Any, Any, Any], int] = {}
        locations: dict[tuple[Any, Any, Any], str] = {}
        for index, relationship in enumerate(graph.relationships):
            if not all(
                _non_empty_string(value)
                for value in (relationship.source, relationship.type, relationship.target)
            ):
                continue
            identity = (relationship.source, relationship.type, relationship.target)
            counts[identity] = counts.get(identity, 0) + 1
            location = _relationship_location(index, relationship.id)
            locations[identity] = min(locations.get(identity, location), location)
        return tuple(
            Finding(
                self.rule_id,
                Severity.WARNING,
                f"Duplicate Relationship: {source!r} {relationship_type!r} {target!r}",
                locations[(source, relationship_type, target)],
            )
            for source, relationship_type, target in sorted(
                (identity for identity, count in counts.items() if count > 1),
                key=lambda identity: tuple(repr(value) for value in identity),
            )
        )


@dataclass(frozen=True, slots=True)
class SelfRelationshipNotAllowedRule:
    rule_id: str = "IKG304"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        return tuple(
            Finding(
                self.rule_id,
                Severity.ERROR,
                "Self Relationship is not allowed",
                _relationship_location(index, relationship.id),
            )
            for index, relationship in enumerate(graph.relationships)
            if _non_empty_string(relationship.type)
            and _non_empty_string(relationship.source)
            and _non_empty_string(relationship.target)
            and relationship.type in RELATIONSHIP_TYPES
            and relationship.source == relationship.target
        )


@dataclass(frozen=True, slots=True)
class InvalidRelationshipDirectionRule:
    rule_id: str = "IKG305"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        entities = {
            entity.identifier: entity
            for entity in graph.entities
            if _non_empty_string(entity.identifier)
        }
        findings: list[Finding] = []
        for index, relationship in enumerate(graph.relationships):
            if not all(
                _non_empty_string(value)
                for value in (relationship.type, relationship.source, relationship.target)
            ):
                continue
            allowed_directions = RELATIONSHIP_DIRECTIONS.get(relationship.type)
            source = entities.get(relationship.source)
            target = entities.get(relationship.target)
            if allowed_directions is None or source is None or target is None:
                continue
            direction = (source.entity_type, target.entity_type)
            if direction not in allowed_directions:
                findings.append(
                    Finding(
                        self.rule_id,
                        Severity.ERROR,
                        f"Invalid Relationship direction: {direction[0]!r} -> {direction[1]!r}",
                        _relationship_location(index, relationship.id),
                    )
                )
        return tuple(findings)


def core_rules() -> tuple[object, ...]:
    """Return the accepted core validation rules in stable order."""
    return (
        MissingRequiredPropertyRule(),
        InvalidPropertyTypeRule(),
        UnknownPropertyRule(),
        InvalidEntityTypeRule(),
        DuplicateIdentifierRule(),
        InvalidIdentifierFormatRule(),
        ReservedIdentifierRule(),
        DeprecatedIdentifierRule(),
        MissingParentRule(),
        InvalidParentTypeRule(),
        MultipleParentsRule(),
        HierarchyCycleRule(),
        OrphanEntityRule(),
        InvalidHierarchyLevelRule(),
        UnknownRelationshipTypeRule(),
        MissingTargetEntityRule(),
        MissingSourceEntityRule(),
        DuplicateRelationshipRule(),
        SelfRelationshipNotAllowedRule(),
        InvalidRelationshipDirectionRule(),
    )
