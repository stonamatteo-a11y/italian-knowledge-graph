"""Export ontology nodes and edges to CSV files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ontology.build import build_graph


def export_csv(output_dir: Path) -> None:
    nodes, edges = build_graph()
    output_dir.mkdir(parents=True, exist_ok=True)

    with (output_dir / "nodes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "label", "type", "parent_id", "description", "language"],
        )
        writer.writeheader()
        writer.writerows(nodes.values())

    with (output_dir / "edges.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "target", "relation"])
        writer.writeheader()
        writer.writerows(edges)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("datasets"))
    args = parser.parse_args()
    export_csv(args.output_dir)


if __name__ == "__main__":
    main()
