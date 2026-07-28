"""Export ontology nodes and edges as JSON Lines files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ontology import build_graph


def export_jsonl(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    nodes_path = output_dir / "nodes.jsonl"
    edges_path = output_dir / "edges.jsonl"
    nodes, edges = build_graph()

    with nodes_path.open("w", encoding="utf-8") as handle:
        for node in nodes.values():
            handle.write(json.dumps(node, ensure_ascii=False) + "\n")

    with edges_path.open("w", encoding="utf-8") as handle:
        for edge in edges:
            handle.write(json.dumps(edge, ensure_ascii=False) + "\n")

    return nodes_path, edges_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("datasets"),
        help="Directory for generated JSONL files.",
    )
    args = parser.parse_args()
    nodes_path, edges_path = export_jsonl(args.output_dir)
    print(f"Wrote {nodes_path}")
    print(f"Wrote {edges_path}")


if __name__ == "__main__":
    main()
