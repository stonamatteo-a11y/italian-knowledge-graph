from ontology import build_graph


def test_seed_counts() -> None:
    nodes, edges = build_graph()
    assert len(nodes) == 1229
    assert len(edges) == 1181

    by_type: dict[str, int] = {}
    for node in nodes.values():
        by_type[node["type"]] = by_type.get(node["type"], 0) + 1

    assert by_type == {
        "macroarea": 48,
        "area": 471,
        "sottoarea": 710,
    }


def test_every_non_root_node_has_a_parent() -> None:
    nodes, _ = build_graph()
    for node in nodes.values():
        if node["type"] == "macroarea":
            assert node["parent_id"] is None
        else:
            assert node["parent_id"] in nodes
