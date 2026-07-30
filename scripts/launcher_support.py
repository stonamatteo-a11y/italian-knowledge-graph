"""Standard-library checks shared by the IKG platform launchers."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import socket
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path

MINIMUM_PYTHON = (3, 10)
LOCAL_HOST = "127.0.0.1"
REQUIRED_MODULES = ("src.editor", "fastapi", "uvicorn")
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def supported_version(version: tuple[int, ...]) -> bool:
    """Return whether a Python version can run IKG."""
    return version >= MINIMUM_PYTHON


def validate_port(port: int) -> int:
    """Validate a TCP port number."""
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    return port


def port_is_available(port: int, host: str = LOCAL_HOST) -> bool:
    """Check whether the local editor address can be bound exclusively."""
    validate_port(port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        try:
            server.bind((host, port))
        except OSError:
            return False
    return True


def project_is_runnable() -> bool:
    """Check the installed editor and its declared runtime dependencies."""
    if str(REPOSITORY_ROOT) not in sys.path:
        sys.path.insert(0, str(REPOSITORY_ROOT))
    if not all(importlib.util.find_spec(module) is not None for module in REQUIRED_MODULES):
        return False
    try:
        importlib.import_module("src.editor.__main__")
    except ImportError:
        return False
    return True


def wait_for_server(
    port: int,
    *,
    host: str = LOCAL_HOST,
    attempts: int = 100,
    interval: float = 0.1,
) -> bool:
    """Wait deterministically for the local HTTP server to answer."""
    validate_port(port)
    url = f"http://{host}:{port}/"
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=0.25) as response:
                if response.status < 500:
                    return True
        except (OSError, urllib.error.URLError):
            time.sleep(interval)
    return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("version")
    commands.add_parser("project")
    port = commands.add_parser("port")
    port.add_argument("port", type=int)
    wait = commands.add_parser("wait")
    wait.add_argument("port", type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "version":
        print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return 0 if supported_version(sys.version_info[:3]) else 1
    if args.command == "project":
        return 0 if project_is_runnable() else 1
    if args.command == "port":
        try:
            available = port_is_available(args.port)
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 2
        return 0 if available else 1
    return 0 if wait_for_server(args.port) else 1


if __name__ == "__main__":
    raise SystemExit(main())
