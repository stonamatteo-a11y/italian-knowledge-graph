"""Immutable dataset records shared by generators and exporters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DatasetRelationship:
    id: str
    type: str
    source: str
    target: str


@dataclass(frozen=True, slots=True)
class DatasetRecord:
    entity_id: str
    entity_type: str
    label: str
    parent: str | None
    relationships: tuple[DatasetRelationship, ...]
