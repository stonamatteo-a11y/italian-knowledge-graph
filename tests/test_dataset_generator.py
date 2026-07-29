import csv
import json

from ikg.dataset import CsvExporter, DatasetGenerator, JsonlExporter
from ikg.graph import Entity, KnowledgeGraph, Relationship


def _graph() -> KnowledgeGraph:
    return KnowledgeGraph(
        entities=(
            Entity("m1", "Macroarea", "Scienze"),
            Entity("a1", "Area", "Fisica", "m1"),
            Entity("s1", "Sottoarea", "Meccanica", "a1"),
        ),
        relationships=(
            Relationship("r2", "CONTAINS", "a1", "s1"),
            Relationship("r1", "CONTAINS", "m1", "a1"),
        ),
    )


def test_jsonl_export(tmp_path) -> None:
    output = tmp_path / "dataset.jsonl"

    JsonlExporter().export(DatasetGenerator(_graph()).generate(), output)

    records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert [record["entity_id"] for record in records] == ["a1", "m1", "s1"]
    assert tuple(records[0]) == (
        "entity_id",
        "entity_type",
        "label",
        "parent",
        "relationships",
    )


def test_csv_export(tmp_path) -> None:
    output = tmp_path / "dataset.csv"

    CsvExporter().export(DatasetGenerator(_graph()).generate(), output)

    with output.open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    assert [record["entity_id"] for record in records] == ["a1", "m1", "s1"]
    assert json.loads(records[0]["relationships"]) == [
        {"id": "r2", "type": "CONTAINS", "source": "a1", "target": "s1"},
        {"id": "r1", "type": "CONTAINS", "source": "m1", "target": "a1"},
    ]


def test_graph_relationships_are_included_in_stable_order() -> None:
    records = DatasetGenerator(_graph()).generate()

    area = records[0]
    assert [relationship.id for relationship in area.relationships] == ["r2", "r1"]


def test_empty_graph_exports_deterministically(tmp_path) -> None:
    records = DatasetGenerator(KnowledgeGraph(entities=())).generate()
    jsonl = tmp_path / "empty.jsonl"
    csv_output = tmp_path / "empty.csv"

    JsonlExporter().export(records, jsonl)
    CsvExporter().export(records, csv_output)

    assert jsonl.read_bytes() == b""
    assert csv_output.read_text(encoding="utf-8") == (
        "entity_id,entity_type,label,parent,relationships\n"
    )


def test_repeated_exports_are_identical(tmp_path) -> None:
    records = DatasetGenerator(_graph()).generate()

    for exporter, suffix in ((JsonlExporter(), "jsonl"), (CsvExporter(), "csv")):
        first = tmp_path / f"first.{suffix}"
        second = tmp_path / f"second.{suffix}"
        exporter.export(records, first)
        exporter.export(records, second)
        assert first.read_bytes() == second.read_bytes()


def test_output_is_independent_of_graph_collection_order(tmp_path) -> None:
    graph = _graph()
    reordered = KnowledgeGraph(
        entities=tuple(reversed(graph.entities)),
        relationships=tuple(reversed(graph.relationships)),
    )
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"

    JsonlExporter().export(DatasetGenerator(graph).generate(), first)
    JsonlExporter().export(DatasetGenerator(reordered).generate(), second)

    assert first.read_bytes() == second.read_bytes()
