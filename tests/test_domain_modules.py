"""Regression tests for the domain-oriented ontology migration."""

from ontology.domains import DOMAIN_NODE_GROUPS, NODES


def test_domain_modules_cover_the_complete_seed() -> None:
    assert len(DOMAIN_NODE_GROUPS) == 8
    assert len(NODES) == 1229


def test_domain_nodes_are_unique() -> None:
    identifiers = [node["id"] for node in NODES]
    assert len(identifiers) == len(set(identifiers))


def test_domain_hierarchy_is_closed() -> None:
    identifiers = {node["id"] for node in NODES}
    for node in NODES:
        parent_id = node["parent_id"]
        assert parent_id is None or parent_id in identifiers
