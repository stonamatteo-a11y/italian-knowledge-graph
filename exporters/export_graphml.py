"""Export ontology to a dependency-free GraphML document."""

from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from ontology.build import build_graph


def export_graphml(output_file: Path) -> None:
    nodes, edges = build_graph()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
        '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
        '  <key id="type" for="node" attr.name="type" attr.type="string"/>',
        '  <key id="description" for="node" attr.name="description" attr.type="string"/>',
        '  <key id="relation" for="edge" attr.name="relation" attr.type="string"/>',
        '  <graph id="IKG" edgedefault="directed">',
    ]

    for node in nodes.values():
        lines.extend(
            [
                f'    <node id="{escape(node["id"])}">',
                f'      <data key="label">{escape(node["label"])}</data>',
                f'      <data key="type">{escape(node["type"])}</data>',
                f'      <data key="description">{escape(node["description"])}</data>',
                '    </node>',
            ]
        )

    for index, edge in enumerate(edges):
        lines.extend(
            [
                f'    <edge id="e{index}" source="{escape(edge["source"])}" target="{escape(edge["target"])}">',
                f'      <data key="relation">{escape(edge["relation"])}</data>',
                '    </edge>',
            ]
        )

    lines.extend(['  </graph>', '</graphml>'])
    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("datasets/ontology.graphml"))
    args = parser.parse_args()
    export_graphml(args.output)


if __name__ == "__main__":
    main()
