#!/bin/sh

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
"$SCRIPT_DIR/start-ikg.sh" "$@"
STATUS=$?
if [ "$STATUS" -ne 0 ]; then
    printf '\nIKG could not start (exit code %s).\n' "$STATUS" >&2
    printf 'Press Return to close this window.'
    read -r _
fi
exit "$STATUS"
