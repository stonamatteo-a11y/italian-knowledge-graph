"""Canonical in-memory graph models and JSON loading."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CANONICAL_ENTITY_PROPERTIES = frozenset({"id", "type", "label", "parent"})
CANONICAL_RELATIONSHIP_PROPERTIES = frozenset({"id", "type", "source", "target"})


@dataclass(frozen=True, slots=True)
class Entity:
    identifier: Any
    entity_type: Any
    label: Any
    parent: Any = None
    unknown_properties: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Relationship:
    id: Any
    type: Any
    source: Any
    target: Any
    unknown_properties: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class KnowledgeGraph:
    entities: tuple[Entity, ...]
    relationships: tuple[Relationship, ...] = ()


def load_graph(path: str | Path) -> KnowledgeGraph:
    """Load a canonical graph from a minimal JSON document.

    Expected shape::

        {
            "entities": [{"id": "...", "type": "...", "label": "...", "parent": null}],
            "relationships": [
                {"id": "...", "type": "CONTAINS", "source": "...", "target": "..."}
            ],
        }

    Values are preserved without coercion so schema rules can report invalid
    property types rather than turning them into loader failures. The
    ``relationships`` collection is optional for compatibility with entity-only
    graph documents.
    """
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        payload: Any = json.load(handle)

    if not isinstance(payload, dict) or not isinstance(payload.get("entities"), list):
        raise ValueError("Expected a JSON object containing an 'entities' list")

    entities: list[Entity] = []
    for index, raw in enumerate(payload["entities"]):
        if not isinstance(raw, dict):
            raise ValueError(f"entities[{index}] must be an object")
        unknown = tuple(sorted(str(key) for key in raw if key not in CANONICAL_ENTITY_PROPERTIES))
        entities.append(
            Entity(
                identifier=raw.get("id"),
                entity_type=raw.get("type"),
                label=raw.get("label"),
                parent=raw.get("parent"),
                unknown_properties=unknown,
            )
        )

    raw_relationships = payload.get("relationships", [])
    if not isinstance(raw_relationships, list):
        raise ValueError("'relationships' must be a list")

    relationships: list[Relationship] = []
    for index, raw in enumerate(raw_relationships):
        if not isinstance(raw, dict):
            raise ValueError(f"relationships[{index}] must be an object")
        unknown = tuple(
            sorted(str(key) for key in raw if key not in CANONICAL_RELATIONSHIP_PROPERTIES)
        )
        relationships.append(
            Relationship(
                id=raw.get("id"),
                type=raw.get("type"),
                source=raw.get("source"),
                target=raw.get("target"),
                unknown_properties=unknown,
            )
        )

    return KnowledgeGraph(entities=tuple(entities), relationships=tuple(relationships))
