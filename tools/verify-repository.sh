#!/usr/bin/env bash
# Location: tools/verify-repository.sh
# Purpose: fail closed on repository layout and published directory restrictions.
# Functions: none; branchless command wiring.
# Calls: repository_checks.validate_repository.
# Imports: none.
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python -I -c 'import sys; sys.path.insert(0, "tools"); from repository_checks import validate_repository; print(validate_repository("."))'
