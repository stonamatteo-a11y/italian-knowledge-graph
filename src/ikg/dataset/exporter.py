"""Shared dataset exporter contract and record mapping."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from .models import DatasetRecord


class DatasetExporter(Protocol):
    def export(self, records: Iterable[DatasetRecord], output: str | Path) -> None:
        """Write records to the requested output path."""


def record_mapping(record: DatasetRecord) -> dict[str, object]:
    return {
        "entity_id": record.entity_id,
        "entity_type": record.entity_type,
        "label": record.label,
        "parent": record.parent,
        "aliases": list(record.aliases),
        "sources": [dict(source) for source in record.sources],
        "notes": list(record.notes),
        "relationships": [
            {
                "id": relationship.id,
                "type": relationship.type,
                "source": relationship.source,
                "target": relationship.target,
            }
            for relationship in record.relationships
        ],
    }
