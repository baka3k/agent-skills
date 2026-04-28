#!/bin/bash
# Agent Skills Kit - shell wrapper for Python installer

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

detect_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        echo "python"
    else
        echo ""
    fi
}

PYTHON_BIN="$(detect_python)"
if [ -z "$PYTHON_BIN" ]; then
    echo "Error: Python is required but not found (python3/python)." >&2
    exit 1
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/install_agent_kit.py" "$@"
