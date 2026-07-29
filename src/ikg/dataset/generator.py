"""Build deterministic dataset records from a validated Knowledge Graph."""

from __future__ import annotations

from ikg.graph import KnowledgeGraph

from .models import DatasetRecord, DatasetRelationship


class DatasetGenerator:
    """Convert a validated graph into stable, exporter-neutral records."""

    def __init__(self, graph: KnowledgeGraph) -> None:
        self._graph = graph

    def generate(self) -> tuple[DatasetRecord, ...]:
        relationships = tuple(
            sorted(
                self._graph.relationships,
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
                relationships=tuple(relationships_by_entity.get(entity.identifier, ())),
            )
            for entity in sorted(self._graph.entities, key=lambda item: item.identifier)
        )
