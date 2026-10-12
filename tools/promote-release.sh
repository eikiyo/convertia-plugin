#!/usr/bin/env bash
# Location: tools/promote-release.sh
# Purpose: promote only a checked candidate accepted and smoke-tested on both hosts.
# Functions: none; branchless command wiring.
# Calls: promotion.promote_release; evidence is read from an external local file.
# Imports: none.
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python -I -c 'import sys; sys.path.insert(0,"tools"); from promotion import promote_release; print(promote_release(".", *sys.argv[1:]))' "$@"
