"""Build the in-memory ontology graph from the preserved seed."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .seed_compressed import AREAS, MACROAREAS, SUBAREAS


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    type: str
    parent_id: str | None
    description: str
    language: str = "it"


def build_graph() -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    """Return node and edge collections from the seed data."""
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []

    def add_node(
        node_id: str,
        label: str,
        node_type: str,
        parent_id: str | None,
        description: str,
    ) -> None:
        if node_id in nodes:
            raise ValueError(f"Duplicate node ID: {node_id}")
        node = Node(node_id, label, node_type, parent_id, description)
        nodes[node_id] = asdict(node)
        if parent_id is not None:
            edges.append(
                {"source": parent_id, "target": node_id, "relation": "CONTAINS"}
            )

    for node_id, label, description in MACROAREAS:
        add_node(node_id, label, "macroarea", None, description)

    for parent_id, children in AREAS:
        for node_id, label, description in children:
            add_node(node_id, label, "area", parent_id, description)

    for parent_id, children in SUBAREAS:
        for node_id, label, description in children:
            add_node(node_id, label, "sottoarea", parent_id, description)

    return nodes, edges
