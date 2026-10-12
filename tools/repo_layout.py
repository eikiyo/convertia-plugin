# Location: tools/repo_layout.py
# Purpose: resolve the single canonical plugin directory for repository callers.
# Functions: plugin_root.
# Calls: filesystem directory checks only.
# Imports: pathlib.
from pathlib import Path

PLUGIN_PATH = 'plugins/convertia'


def plugin_root(root):
    root = Path(root)
    nested = root / PLUGIN_PATH
    return nested if nested.is_dir() else root
