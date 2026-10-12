# Location: tools/verify.py
# Purpose: stable command entrypoint with observable release validation failures.
# Functions: main.
# Calls: release_checks.validate, frontmatter_regression.frontmatter_selftest.
# Imports: os, sys, pathlib, release_checks, frontmatter_regression.
import os
import sys
import subprocess
from pathlib import Path
from release_checks import validate
from frontmatter_regression import frontmatter_selftest


def main(args=None, root=None):
    args = sys.argv[1:] if args is None else args
    root = Path.cwd() if root is None else root
    try:
        if args == ['--self-test']:
            frontmatter_selftest(root)
        elif args:
            raise ValueError('Usage: bash tools/verify.sh [--self-test]')
        else:
            print(validate(root, os.environ.get('PREVIOUS_VERSION')))
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    return 0
