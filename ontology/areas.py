"""Area data assembled from domain-oriented ontology modules."""

from __future__ import annotations

from collections import defaultdict

from .domains import NODES

_grouped: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
_parent_order: list[str] = []

for node in NODES:
    if node["type"] != "area":
        continue
    parent_id = str(node["parent_id"])
    if parent_id not in _grouped:
        _parent_order.append(parent_id)
    _grouped[parent_id].append(
        (str(node["id"]), str(node["label"]), str(node["description"]))
    )

AREAS = [(parent_id, _grouped[parent_id]) for parent_id in _parent_order]

__all__ = ["AREAS"]
