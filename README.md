# Convertia source repository

The canonical plugin lives in [plugins/convertia](plugins/convertia). Read its [README](plugins/convertia/README.md) for commands and usage.

Tests, release tools and maintainer instructions stay at the repository root. The generated `distribution` branch contains only the checked plugin and is never edited directly. Claude follows that branch; ChatGPT receives the matching checked CI archive.

A green candidate build is not hosted acceptance. Both hosts need matching installation and smoke-test evidence before release promotion. See [MAINTAINING.md](MAINTAINING.md), [TESTING.md](TESTING.md) and [CLAUDE.md](CLAUDE.md).
