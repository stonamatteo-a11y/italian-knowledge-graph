from __future__ import annotations

import http.server
import socket
import threading
from pathlib import Path

import pytest

from scripts.launcher_support import (
    LOCAL_HOST,
    port_is_available,
    supported_version,
    validate_port,
    wait_for_server,
)

ROOT = Path(__file__).resolve().parents[1]


def _text(filename: str) -> str:
    return (ROOT / filename).read_text(encoding="utf-8")


def test_shared_launcher_version_and_port_validation() -> None:
    assert supported_version((3, 10, 0))
    assert supported_version((3, 13, 1))
    assert not supported_version((3, 9, 99))
    assert validate_port(7777) == 7777
    with pytest.raises(ValueError):
        validate_port(0)
    with pytest.raises(ValueError):
        validate_port(65536)


def test_shared_launcher_checks_port_on_loopback_only() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as occupied:
        occupied.bind((LOCAL_HOST, 0))
        port = occupied.getsockname()[1]
        assert not port_is_available(port)
    assert port_is_available(port)


def test_shared_launcher_waits_for_local_server_and_times_out() -> None:
    server = http.server.ThreadingHTTPServer((LOCAL_HOST, 0), http.server.SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert wait_for_server(server.server_port, attempts=5, interval=0.01)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    assert not wait_for_server(server.server_port, attempts=1, interval=0)


def test_windows_launcher_handles_root_interpreters_options_and_exit_codes() -> None:
    powershell = _text("start-ikg.ps1")

    assert "Split-Path -Parent $MyInvocation.MyCommand.Path" in powershell
    assert powershell.index('@{ Name = "py"') < powershell.index('@{ Name = "python"')
    assert powershell.index('@{ Name = "python"') < powershell.index('@{ Name = "python3"')
    assert '"--port"' in powershell
    assert '"--no-browser"' in powershell
    assert '"--check-only"' in powershell
    assert "http://127.0.0.1:$Port" in powershell
    assert powershell.count('Start-Process "http://127.0.0.1:$Port"') == 1
    assert "$ServerProcess.Kill($true)" in powershell
    assert "exit $ExitCode" in powershell
    assert "Python 3.10 or newer is required" in powershell
    assert "pip install --no-deps --no-build-isolation -e ." in powershell


def test_windows_batch_is_a_minimal_safe_wrapper() -> None:
    batch = _text("start-ikg.bat")

    assert '"%~dp0start-ikg.ps1" %*' in batch
    assert "-NoProfile" in batch
    assert "-ExecutionPolicy Bypass" in batch
    assert "pause" in batch
    assert "exit /b %IKG_EXIT_CODE%" in batch


def test_shell_launcher_supports_macos_linux_and_signals() -> None:
    shell = _text("start-ikg.sh")

    assert 'ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)' in shell
    assert "for candidate in python3 python" in shell
    assert "Darwin)" in shell
    assert "Linux)" in shell
    assert 'open "$URL"' in shell
    assert 'xdg-open "$URL"' in shell
    assert 'gio open "$URL"' in shell
    assert shell.count('open "$URL"') == 3
    assert "--port" in shell
    assert "--no-browser" in shell
    assert "--check-only" in shell
    assert 'URL="http://127.0.0.1:$PORT"' in shell
    assert "trap interrupt INT TERM" in shell
    assert 'kill "$SERVER_PID"' in shell
    assert 'exit "$SERVER_STATUS"' in shell
    assert "Python 3.10 or newer is required" in shell
    assert "pip install --no-deps --no-build-isolation -e ." in shell


def test_macos_command_wrapper_forwards_arguments_and_pauses_only_on_error() -> None:
    command = _text("start-ikg.command")

    assert 'SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)' in command
    assert '"$SCRIPT_DIR/start-ikg.sh" "$@"' in command
    assert 'if [ "$STATUS" -ne 0 ]' in command
    assert "read -r _" in command
    assert 'exit "$STATUS"' in command


def test_launchers_do_not_download_install_python_or_expose_the_server() -> None:
    combined = "\n".join(
        _text(filename)
        for filename in ("start-ikg.ps1", "start-ikg.bat", "start-ikg.sh", "start-ikg.command")
    ).casefold()

    for forbidden in (
        "curl ",
        "wget ",
        "winget ",
        "homebrew",
        "brew install",
        "apt ",
        "git ",
        "0.0.0.0",
    ):
        assert forbidden not in combined
