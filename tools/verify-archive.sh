#!/usr/bin/env bash
# Location: tools/verify-archive.sh
# Purpose: run archive validation from the maintainer checkout.
# Functions: none; branchless command wiring.
# Calls: archive_checks.main in isolated Python.
# Imports: none.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -I -c 'import sys; sys.path.insert(0, "tools"); from archive_checks import main; raise SystemExit(main())' "$@"
