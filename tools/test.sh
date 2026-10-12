#!/usr/bin/env bash
# Location: tools/test.sh
# Purpose: run deterministic tests and require complete statement/branch coverage.
# Functions: none; branchless command wiring.
# Calls: isolated Python test environment.
# Imports: none.
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python -m coverage run -m pytest "$@"
.venv/bin/python -m coverage report
.venv/bin/python -m coverage json -o coverage.json
