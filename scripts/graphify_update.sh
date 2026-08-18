#!/usr/bin/env bash
# Runs `graphify update .` bounded by a timeout.
#
# graphify's AI-community-summarization step can hang for 15-20+ minutes
# on some graph shapes. Never let this block a push indefinitely — bound it,
# and degrade to "push with a stale graph, flagged" on timeout.
#
# Usage: scripts/graphify_update.sh [timeout_seconds]

set -uo pipefail

TIMEOUT_SECONDS="${1:-120}"

if command -v timeout >/dev/null 2>&1; then
    TIMEOUT_CMD="timeout"
elif command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_CMD="gtimeout"
else
    echo "WARNING: no 'timeout'/'gtimeout' found (brew install coreutils for gtimeout)." >&2
    echo "Running graphify update . unbounded — it may hang." >&2
    exec graphify update .
fi

"$TIMEOUT_CMD" "$TIMEOUT_SECONDS" graphify update .
status=$?

if [ "$status" -eq 124 ]; then
    echo "" >&2
    echo "graphify update . did not finish within ${TIMEOUT_SECONDS}s — killed." >&2
    echo "Proceeding WITHOUT a refreshed graph. graphify-out/ is now stale." >&2
    exit 0
fi

exit "$status"
