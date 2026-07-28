"""Validate ontology structure and report consistency errors."""

from __future__ import annotations

from collections import Counter

from ontology import build_graph


def validate() -> list[str]:
    errors: list[str] = []
    nodes, edges = build_graph()
    expected_parent_type = {"area": "macroarea", "sottoarea": "area"}

    for node in nodes.values():
        parent_id = node["parent_id"]
        if parent_id is None:
            if node["type"] != "macroarea":
                errors.append(f'{node["id"]}: only macroareas may have no parent')
            continue

        parent = nodes.get(parent_id)
        if parent is None:
            errors.append(f'{node["id"]}: missing parent {parent_id}')
            continue

        required = expected_parent_type.get(node["type"])
        if required and parent["type"] != required:
            errors.append(
                f'{node["id"]}: expected parent type {required}, got {parent["type"]}'
            )

    edge_pairs = {(edge["source"], edge["target"]) for edge in edges}
    for node in nodes.values():
        if node["parent_id"] is not None:
            pair = (node["parent_id"], node["id"])
            if pair not in edge_pairs:
                errors.append(f'{node["id"]}: missing CONTAINS edge')

    counts = Counter(node["type"] for node in nodes.values())
    print(
        f'Validated {len(nodes)} nodes and {len(edges)} edges '
        f'({counts["macroarea"]} macroareas, {counts["area"]} areas, '
        f'{counts["sottoarea"]} subareas).'
    )
    return errors


if __name__ == "__main__":
    issues = validate()
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        raise SystemExit(1)
    print("Ontology validation passed.")
