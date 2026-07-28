"""Export Neo4j-compatible node and relationship CSV files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ontology.build import build_graph


def export_neo4j(output_dir: Path) -> None:
    nodes, edges = build_graph()
    output_dir.mkdir(parents=True, exist_ok=True)

    with (output_dir / "neo4j_nodes.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["id:ID", "label", "type:LABEL", "parent_id", "description", "language"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for node in nodes.values():
            writer.writerow(
                {
                    "id:ID": node["id"],
                    "label": node["label"],
                    "type:LABEL": node["type"],
                    "parent_id": node["parent_id"] or "",
                    "description": node["description"],
                    "language": node["language"],
                }
            )

    with (output_dir / "neo4j_relationships.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        fieldnames = [":START_ID", ":END_ID", ":TYPE"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for edge in edges:
            writer.writerow(
                {
                    ":START_ID": edge["source"],
                    ":END_ID": edge["target"],
                    ":TYPE": edge["relation"],
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("datasets/neo4j"))
    args = parser.parse_args()
    export_neo4j(args.output_dir)


if __name__ == "__main__":
    main()
