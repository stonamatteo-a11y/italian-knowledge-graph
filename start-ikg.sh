#!/usr/bin/env sh

set -u

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PORT=7777
NO_BROWSER=0
CHECK_ONLY=0
SERVER_PID=

fail() {
    printf 'IKG launcher error: %s\n' "$1" >&2
    exit "${2:-1}"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --port)
            [ "$#" -ge 2 ] || fail "--port requires a value" 2
            PORT=$2
            shift 2
            ;;
        --no-browser)
            NO_BROWSER=1
            shift
            ;;
        --check-only)
            CHECK_ONLY=1
            shift
            ;;
        *)
            fail "unknown option: $1" 2
            ;;
    esac
done

case "$PORT" in
    ''|*[!0-9]*) fail "port must be a number" 2 ;;
esac

PYTHON=
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" "$ROOT_DIR/scripts/launcher_support.py" version >/dev/null 2>&1; then
            PYTHON=$candidate
            break
        fi
    fi
done

SYSTEM=$(uname -s 2>/dev/null || printf 'Unknown')
if [ -z "$PYTHON" ]; then
    case "$SYSTEM" in
        Darwin) fail "Python 3.10 or newer is required. Install Python, then run this launcher again." ;;
        Linux) fail "Python 3.10 or newer is required. Install it using your system's documented method." ;;
        *) fail "Python 3.10 or newer is required on macOS or Linux." ;;
    esac
fi

PYTHON_VERSION=$("$PYTHON" "$ROOT_DIR/scripts/launcher_support.py" version)
printf 'Python: %s (%s)\n' "$PYTHON_VERSION" "$PYTHON"
printf 'Repository: %s\n' "$ROOT_DIR"
printf 'URL: http://127.0.0.1:%s\n' "$PORT"

cd "$ROOT_DIR" || fail "cannot enter repository directory"

if ! "$PYTHON" scripts/launcher_support.py project; then
    if [ "$CHECK_ONLY" -eq 1 ]; then
        fail "the project is not installed or runtime dependencies are unavailable"
    fi
    printf 'Preparing the local editable installation...\n'
    "$PYTHON" -m pip install --no-deps --no-build-isolation -e . ||
        fail "editable installation failed; no remote packages were downloaded"
    "$PYTHON" scripts/launcher_support.py project ||
        fail "FastAPI or Uvicorn is missing. Install project requirements manually and retry."
fi

"$PYTHON" scripts/launcher_support.py port "$PORT" ||
    fail "127.0.0.1:$PORT is already in use or unavailable"

if [ "$CHECK_ONLY" -eq 1 ]; then
    printf 'Check completed successfully. No server or browser was started.\n'
    exit 0
fi

cleanup() {
    status=$?
    trap - INT TERM EXIT
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    exit "$status"
}

interrupt() {
    trap - INT TERM EXIT
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    exit 130
}

trap cleanup EXIT
trap interrupt INT TERM

"$PYTHON" run_editor.py --port "$PORT" &
SERVER_PID=$!

if ! "$PYTHON" scripts/launcher_support.py wait "$PORT"; then
    wait "$SERVER_PID" 2>/dev/null
    status=$?
    fail "the editor did not become available (server exit code $status)"
fi

URL="http://127.0.0.1:$PORT"
if [ "$NO_BROWSER" -eq 0 ]; then
    case "$SYSTEM" in
        Darwin)
            open "$URL" >/dev/null 2>&1 || printf 'Open manually: %s\n' "$URL"
            ;;
        Linux)
            if command -v xdg-open >/dev/null 2>&1; then
                xdg-open "$URL" >/dev/null 2>&1 || printf 'Open manually: %s\n' "$URL"
            elif command -v gio >/dev/null 2>&1; then
                gio open "$URL" >/dev/null 2>&1 || printf 'Open manually: %s\n' "$URL"
            else
                printf 'No browser launcher found. Open manually: %s\n' "$URL"
            fi
            ;;
        *)
            printf 'Unsupported browser launcher. Open manually: %s\n' "$URL"
            ;;
    esac
fi

wait "$SERVER_PID"
SERVER_STATUS=$?
SERVER_PID=
trap - INT TERM EXIT
exit "$SERVER_STATUS"
