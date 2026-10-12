#!/usr/bin/env bash
# Location: tools/publish-distribution.sh
# Purpose: publish the checked main subtree as the derived distribution branch.
# Functions: none; branchless command wiring.
# Calls: distribution.publish_distribution.
# Imports: none.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -I -c 'import sys; sys.path.insert(0, "tools"); from distribution import publish_distribution; print(publish_distribution(".", sys.argv[1]))' "$1"
