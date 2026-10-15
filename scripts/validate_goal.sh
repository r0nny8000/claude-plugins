#!/bin/sh
# Plugin users' machines vary: some only ship `python3` (macOS, Debian/Ubuntu).
# Prefer `python`, fall back to `python3`.
if command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    PYTHON=python3
fi
exec "$PYTHON" "${0%/*}/validate_goal.py" "$@"
