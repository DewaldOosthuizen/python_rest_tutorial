#!/usr/bin/env bash
# Lint script — mirrors CI exactly so "passes locally" == "passes in CI".
#
# Usage:
#   ./scripts/lint.sh          # check only (same as CI)
#   ./scripts/lint.sh --fix    # auto-fix then check

set -euo pipefail

FIX=0
for arg in "$@"; do
    [[ "$arg" == "--fix" ]] && FIX=1
done

echo "==> lint"

if [[ $FIX -eq 1 ]]; then
    echo "--- ruff format (fix) ---"
    ruff format web/ tests/
    echo "--- ruff check --fix ---"
    ruff check web/ tests/ --fix
    echo "--- re-check after fixes ---"
fi

echo "--- ruff check web/ tests/ ---"
ruff check web/ tests/

echo "--- ruff format --check web/ tests/ ---"
ruff format --check web/ tests/

echo "==> All lint checks passed."
