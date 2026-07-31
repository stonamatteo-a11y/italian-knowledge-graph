"""Build deterministic dataset records from a validated Knowledge Graph."""

from __future__ import annotations

from ikg.graph import KnowledgeGraph, Relationship

from .models import DatasetRecord, DatasetRelationship


class DatasetGenerator:
    """Convert a validated graph into stable, exporter-neutral records."""

    def __init__(self, graph: KnowledgeGraph) -> None:
        self._graph = graph

    def generate(self) -> tuple[DatasetRecord, ...]:
        embedded = tuple(
            Relationship(
                id=f"{entity.identifier}:{relation['predicate']}:{relation['target_id']}",
                type=relation["predicate"],
                source=entity.identifier,
                target=relation["target_id"],
            )
            for entity in self._graph.entities
            for relation in entity.relations
        )
        unique = {
            (relationship.source, relationship.type, relationship.target): relationship
            for relationship in (*self._graph.relationships, *embedded)
        }
        relationships = tuple(
            sorted(
                unique.values(),
                key=lambda item: (item.source, item.type, item.target, item.id),
            )
        )
        relationships_by_entity: dict[str, list[DatasetRelationship]] = {}
        for relationship in relationships:
            record = DatasetRelationship(
                id=relationship.id,
                type=relationship.type,
                source=relationship.source,
                target=relationship.target,
            )
            relationships_by_entity.setdefault(relationship.source, []).append(record)
            if relationship.target != relationship.source:
                relationships_by_entity.setdefault(relationship.target, []).append(record)

        return tuple(
            DatasetRecord(
                entity_id=entity.identifier,
                entity_type=entity.entity_type,
                label=entity.label,
                parent=entity.parent,
                aliases=tuple(entity.aliases),
                sources=tuple(dict(source) for source in entity.sources),
                notes=tuple(entity.notes),
                relationships=tuple(relationships_by_entity.get(entity.identifier, ())),
            )
            for entity in sorted(self._graph.entities, key=lambda item: item.identifier)
        )
