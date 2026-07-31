"""Validate converted imports against the complete canonical ontology."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from ikg.metadata import METADATA_FIELDS, canonical_metadata
from scripts.generate_seed import SeedGenerationError, validate_canonical
from validators.validate_ontology import validate_graph

from ..store import LEVELS
from .models import CanonicalNode

TYPE_TO_SECTION = {node_type: section for section, node_type, _ in LEVELS}


@dataclass(frozen=True, slots=True)
class ImportValidation:
    records: dict[str, list[dict[str, Any]]] | None
    nodes_to_add: int
    relationships_to_add: int
    collisions: tuple[str, ...]
    duplicates: tuple[str, ...]
    updates: tuple[str, ...]
    errors: tuple[str, ...]


class ImportValidator:
    def validate(
        self,
        current: dict[str, list[dict[str, Any]]],
        nodes: tuple[CanonicalNode, ...],
    ) -> ImportValidation:
        records = copy.deepcopy(current)
        existing = {
            record["id"]: (section, record)
            for section, values in records.items()
            for record in values
        }
        seen: dict[str, CanonicalNode] = {}
        collisions: list[str] = []
        duplicates: list[str] = []
        errors: list[str] = []
        additions: list[CanonicalNode] = []
        updates: list[str] = []

        for node in nodes:
            if node.identifier in seen:
                duplicates.append(node.identifier)
                continue
            seen[node.identifier] = node
            match = existing.get(node.identifier)
            if match is not None:
                section, record = match
                proposed = node.as_record()
                merged = {**proposed}
                for field in METADATA_FIELDS:
                    merged[field] = [
                        *record.get(field, []),
                        *proposed.get(field, []),  # type: ignore[arg-type]
                    ]
                normalized = canonical_metadata(merged)
                for field, value in normalized.items():
                    if value:
                        merged[field] = value
                    else:
                        merged.pop(field, None)
                if section == TYPE_TO_SECTION[node.node_type] and record == merged:
                    duplicates.append(node.identifier)
                elif (
                    section == TYPE_TO_SECTION[node.node_type]
                    and record["id"] == node.identifier
                    and record["label"] == node.label
                    and record.get("parent_id") == node.parent
                    and record["language"] == node.language
                ):
                    records[section][records[section].index(record)] = merged
                    if record["description"] != node.description:
                        updates.append(
                            f"{node.identifier}: proposed description: {node.description}"
                        )
                    for field in METADATA_FIELDS:
                        before = record.get(field, [])
                        after = merged.get(field, [])
                        if before != after:
                            updates.append(
                                f"{node.identifier}: {field} {len(before)} → {len(after)}"
                            )
                else:
                    collisions.append(node.identifier)
                    errors.append(f"{node.identifier}: conflicts with an existing canonical node")
                continue
            additions.append(node)

        for node in additions:
            records[TYPE_TO_SECTION[node.node_type]].append(node.as_record())
        try:
            validate_canonical(records)
            graph_nodes: dict[str, dict[str, Any]] = {}
            edges: list[dict[str, str]] = []
            for section, node_type, _ in LEVELS:
                for record in records[section]:
                    parent = record.get("parent_id")
                    graph_nodes[record["id"]] = {
                        **record,
                        "type": node_type,
                        "parent_id": parent,
                    }
                    if parent is not None:
                        edges.append(
                            {"source": parent, "target": record["id"], "relation": "CONTAINS"}
                        )
            errors.extend(validate_graph(graph_nodes, edges))
        except SeedGenerationError as exc:
            errors.append(str(exc))

        unique_errors = tuple(sorted(set(errors)))
        return ImportValidation(
            records if not unique_errors else None,
            len(additions),
            sum(node.parent is not None for node in additions),
            tuple(sorted(set(collisions))),
            tuple(sorted(set(duplicates))),
            tuple(sorted(set(updates))),
            unique_errors,
        )
