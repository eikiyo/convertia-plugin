#!/usr/bin/env bash
# Location: tools/verify-official.sh
# Purpose: validate actual extracted runtime files with pinned official tools.
# Functions: none; branchless command wiring.
# Calls: official_checks and Claude Code 2.1.296 strict validator.
# Imports: none.
set -euo pipefail
cd "$(dirname "$0")/.."
unset "${!ANTHROPIC@}"
.venv/bin/python -I -c 'import sys; sys.path.insert(0,"tools"); from official_checks import validate_official; print(validate_official("."))'
.venv/bin/python -I -c 'import sys; sys.path.insert(0,"tools"); from official_checks import validate_official; print(validate_official(sys.argv[1]))' "$1"
npm exec --yes --package=@anthropic-ai/claude-code@2.1.296 -- claude plugin validate .claude-plugin/marketplace.json --strict
npm exec --yes --package=@anthropic-ai/claude-code@2.1.296 -- claude plugin validate plugins/convertia/.claude-plugin/plugin.json --strict
npm exec --yes --package=@anthropic-ai/claude-code@2.1.296 -- claude plugin validate "$1/.claude-plugin/marketplace.json" --strict
npm exec --yes --package=@anthropic-ai/claude-code@2.1.296 -- claude plugin validate "$1/.claude-plugin/plugin.json" --strict
