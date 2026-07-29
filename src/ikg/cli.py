"""Command-line interface for IKG."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .dataset import CsvExporter, DatasetGenerator, JsonlExporter
from .graph import load_graph
from .validator import ValidationEngine
from .validator.builtin import core_rules


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ikg", description="Italian Knowledge Graph tools")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    commands = parser.add_subparsers(dest="command")
    validate = commands.add_parser("validate", help="Validate a canonical Knowledge Graph")
    validate.add_argument("input", type=Path, help="Path to the canonical JSON graph")

    stats = commands.add_parser("stats", help="Show Knowledge Graph statistics")
    stats.add_argument("input", type=Path, help="Path to the canonical JSON graph")

    doctor = commands.add_parser("doctor", help="Check an input file before validation")
    doctor.add_argument("input", type=Path, help="Path to the canonical JSON graph")

    export = commands.add_parser("export", help="Export derived artifacts")
    export_commands = export.add_subparsers(dest="export_command", required=True)
    dataset = export_commands.add_parser("dataset", help="Export a machine-learning dataset")
    dataset.add_argument("--input", required=True, type=Path, help="Canonical JSON graph")
    dataset.add_argument("--format", required=True, choices=("jsonl", "csv"), help="Output format")
    dataset.add_argument("--output", required=True, type=Path, help="Dataset output path")
    return parser


def _load(path: Path):
    try:
        return load_graph(path)
    except (OSError, ValueError) as exc:
        print(f"IKG901 ERROR {exc}")
        return None


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    graph = _load(args.input)
    if graph is None:
        return 3

    if args.command == "export":
        report = ValidationEngine(core_rules()).validate(graph)
        if not report.is_valid:
            for finding in report.findings:
                location = f" [{finding.location}]" if finding.location else ""
                print(f"{finding.rule_id} {finding.severity.value}{location}: {finding.message}")
            return 1
        exporter = JsonlExporter() if args.format == "jsonl" else CsvExporter()
        exporter.export(DatasetGenerator(graph).generate(), args.output)
        return 0

    if args.command == "doctor":
        print(f"OK: loaded {len(graph.entities)} entities from {args.input}")
        return 0

    if args.command == "stats":
        counts = Counter(entity.entity_type for entity in graph.entities)
        print(f"entities: {len(graph.entities)}")
        for entity_type in sorted(counts):
            print(f"{entity_type}: {counts[entity_type]}")
        return 0

    report = ValidationEngine(core_rules()).validate(graph)
    for finding in report.findings:
        location = f" [{finding.location}]" if finding.location else ""
        print(f"{finding.rule_id} {finding.severity.value}{location}: {finding.message}")
    print(
        f"valid={str(report.is_valid).lower()} "
        f"errors={report.error_count} warnings={report.warning_count} info={report.info_count}"
    )
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
