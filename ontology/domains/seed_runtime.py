"""Compatibility helpers used during the domain-module migration.

This module reads the lossless v0.1 seed and exposes selected branches as normal
node dictionaries. Domain modules can therefore be reviewed independently while
preserving exact identifiers, labels, descriptions and ordering.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from ..seed_compressed import AREAS, MACROAREAS, SUBAREAS


def _all_nodes() -> list[dict[str, str | None]]:
    nodes: list[dict[str, str | None]] = []
    for node_id, label, description in MACROAREAS:
        nodes.append({
            "id": node_id,
            "label": label,
            "type": "macroarea",
            "parent_id": None,
            "description": description,
            "language": "it",
        })
    for parent_id, children in AREAS:
        for node_id, label, description in children:
            nodes.append({
                "id": node_id,
                "label": label,
                "type": "area",
                "parent_id": parent_id,
                "description": description,
                "language": "it",
            })
    for parent_id, children in SUBAREAS:
        for node_id, label, description in children:
            nodes.append({
                "id": node_id,
                "label": label,
                "type": "sottoarea",
                "parent_id": parent_id,
                "description": description,
                "language": "it",
            })
    return nodes


_ALL_NODES = _all_nodes()
_CHILDREN: dict[str | None, list[dict[str, str | None]]] = defaultdict(list)
for _node in _ALL_NODES:
    _CHILDREN[_node["parent_id"]].append(_node)


def select_domain_nodes(macroarea_ids: Iterable[str]) -> list[dict[str, str | None]]:
    """Return complete branches rooted at the requested macroarea identifiers."""
    selected: list[dict[str, str | None]] = []
    requested = set(macroarea_ids)
    for macroarea in _CHILDREN[None]:
        if macroarea["id"] not in requested:
            continue
        selected.append(dict(macroarea))
        for area in _CHILDREN[macroarea["id"]]:
            selected.append(dict(area))
            selected.extend(dict(node) for node in _CHILDREN[area["id"]])
    return selected
