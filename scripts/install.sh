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

# Default to enhanced installer so templates are copied by default.
INSTALLER_SCRIPT="$SCRIPT_DIR/install_agent_kit_with_templates.py"

FORCE_CURRENT_DIR=false
if [ "${1:-}" = "." ]; then
    FORCE_CURRENT_DIR=true
    shift
fi

EXTRA_ARGS=()

if [ "$FORCE_CURRENT_DIR" = true ]; then
    echo "Info: install '.' detected. Installing to current directory: $PWD"
    EXTRA_ARGS+=(--scope local --project-root "$PWD")
fi

if [ "$#" -eq 0 ]; then
    EXTRA_ARGS+=(--interactive)
fi

if [ "${#EXTRA_ARGS[@]}" -gt 0 ]; then
    exec "$PYTHON_BIN" "$INSTALLER_SCRIPT" "$@" "${EXTRA_ARGS[@]}"
fi

exec "$PYTHON_BIN" "$INSTALLER_SCRIPT" "$@"
