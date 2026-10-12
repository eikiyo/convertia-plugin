#!/usr/bin/env bash
# Location: tools/verify.sh
# Purpose: launch the shared standard-library release validator.
# Functions: none; branchless command wiring.
# Calls: python3 isolated interpreter and verify.main.
# Imports: none.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -I -c 'import sys; sys.path.insert(0, "tools"); from verify import main; raise SystemExit(main())' "$@"
