"""Export ontology nodes and edges to SQLite."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from ontology.build import build_graph


def export_sqlite(output_file: Path) -> None:
    nodes, edges = build_graph()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(output_file) as connection:
        connection.executescript(
            """
            DROP TABLE IF EXISTS edges;
            DROP TABLE IF EXISTS nodes;
            CREATE TABLE nodes (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                type TEXT NOT NULL,
                parent_id TEXT,
                description TEXT NOT NULL,
                language TEXT NOT NULL
            );
            CREATE TABLE edges (
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                relation TEXT NOT NULL,
                PRIMARY KEY (source, target, relation)
            );
            CREATE INDEX idx_nodes_parent ON nodes(parent_id);
            CREATE INDEX idx_nodes_type ON nodes(type);
            """
        )
        connection.executemany(
            "INSERT INTO nodes VALUES (:id, :label, :type, :parent_id, :description, :language)",
            nodes.values(),
        )
        connection.executemany(
            "INSERT INTO edges VALUES (:source, :target, :relation)", edges
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("datasets/ontology.sqlite"))
    args = parser.parse_args()
    export_sqlite(args.output)


if __name__ == "__main__":
    main()
