#!/bin/bash
# Activate the project's virtual environment
# Usage: source activate.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    echo "✓ Virtual environment activated: $VENV_DIR"
    echo "  Python: $(which python3)"
    echo "  Uvicorn: $(which uvicorn)"
else
    echo "✗ Virtual environment not found at $VENV_DIR"
    echo "  Run: python3 -m venv .venv"
    exit 1
fi
