"""Command-line interface for IKG."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from . import __version__
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
