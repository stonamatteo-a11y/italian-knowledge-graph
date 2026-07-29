"""Command-line interface for IKG."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ikg", description="Italian Knowledge Graph tools")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    commands = parser.add_subparsers(dest="command")
    commands.add_parser("validate", help="Validate the canonical Knowledge Graph")
    commands.add_parser("stats", help="Show Knowledge Graph statistics")
    commands.add_parser("doctor", help="Check project configuration and required inputs")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    parser.error(f"The '{args.command}' command is not implemented yet")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
