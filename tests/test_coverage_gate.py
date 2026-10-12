# Location: tests/test_coverage_gate.py
# Purpose: prove the configured coverage threshold rejects missed code.
# Functions: test_coverage_threshold_control.
# Calls: real coverage CLI with isolated data and source files.
# Imports: pathlib, subprocess, sys, pytest.
from pathlib import Path
import subprocess
import sys
import pytest


@pytest.mark.parametrize('execute,expected', [(False, 2), (True, 0)])
def test_coverage_threshold_control(tmp_path, execute, expected):
    source = tmp_path / 'probe.py'
    body = 'def answer():\n    return 42\n'
    source.write_text(body + ('answer()\n' if execute else 'print("control")\n'))
    data = str(tmp_path / '.coverage')
    root = Path(__file__).resolve().parents[1]
    run = subprocess.run(
        [sys.executable, '-m', 'coverage', 'run', '--data-file=' + data,
         '--source=' + str(tmp_path), str(source)],
        cwd=root, capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    report = subprocess.run(
        [sys.executable, '-m', 'coverage', 'report', '--data-file=' + data],
        cwd=root, capture_output=True, text=True, timeout=30)
    assert report.returncode == expected, report.stdout + report.stderr
    if not execute:
        assert 'less than fail-under=100' in report.stdout
