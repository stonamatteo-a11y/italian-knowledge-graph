"""Initial deterministic validation rules."""

from __future__ import annotations

from dataclasses import dataclass

from ikg.graph import KnowledgeGraph

from .models import Finding, Severity

ALLOWED_TYPES = {"Macroarea", "Area", "Sottoarea", "Concetto"}


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
                if not isinstance(value, str) or not value.strip():
                    findings.append(
                        Finding(self.rule_id, Severity.ERROR, f"Missing required property: {name}", f"entities[{index}]")
                    )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class InvalidEntityTypeRule:
    rule_id: str = "IKG004"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        return tuple(
            Finding(self.rule_id, Severity.ERROR, f"Invalid Entity type: {entity.entity_type!r}", entity.identifier or f"entities[{index}]")
            for index, entity in enumerate(graph.entities)
            if entity.entity_type not in ALLOWED_TYPES
        )


@dataclass(frozen=True, slots=True)
class DuplicateIdentifierRule:
    rule_id: str = "IKG100"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        counts: dict[str, int] = {}
        for entity in graph.entities:
            if isinstance(entity.identifier, str) and entity.identifier:
                counts[entity.identifier] = counts.get(entity.identifier, 0) + 1
        return tuple(
            Finding(self.rule_id, Severity.ERROR, f"Duplicate identifier: {identifier}", identifier)
            for identifier, count in sorted(counts.items())
            if count > 1
        )


@dataclass(frozen=True, slots=True)
class MissingParentRule:
    rule_id: str = "IKG200"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        return tuple(
            Finding(self.rule_id, Severity.ERROR, "Non-root Entity has no parent", entity.identifier)
            for entity in graph.entities
            if entity.entity_type != "Macroarea" and not entity.parent
        )


@dataclass(frozen=True, slots=True)
class HierarchyCycleRule:
    rule_id: str = "IKG203"

    def validate(self, graph: KnowledgeGraph) -> tuple[Finding, ...]:
        parents = {entity.identifier: entity.parent for entity in graph.entities if entity.identifier}
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
        entities = {entity.identifier: entity for entity in graph.entities if entity.identifier}
        orphans: list[str] = []
        for identifier, entity in sorted(entities.items()):
            if entity.entity_type == "Macroarea":
                continue
            visited: set[str] = set()
            current = entity
            while current.entity_type != "Macroarea":
                if current.identifier in visited or not current.parent or current.parent not in entities:
                    orphans.append(identifier)
                    break
                visited.add(current.identifier)
                current = entities[current.parent]
        return tuple(
            Finding(self.rule_id, Severity.ERROR, "Entity is not reachable from a Macroarea", identifier)
            for identifier in orphans
        )


def core_rules() -> tuple[object, ...]:
    """Return the accepted core-rule set in stable ID order."""
    return (
        MissingRequiredPropertyRule(),
        InvalidEntityTypeRule(),
        DuplicateIdentifierRule(),
        MissingParentRule(),
        HierarchyCycleRule(),
        OrphanEntityRule(),
    )
