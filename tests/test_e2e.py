# Location: tests/test_e2e.py
# Purpose: verify real shell execution and optimized-Python validation.
# Functions: run_command, launcher tests and optimized-Python negative controls.
# Calls: bash, Python and git with temporary repository only.
# Imports: os, subprocess, sys, pytest.
import os
import subprocess
import sys
import pytest
from pathlib import Path
from conftest import expected_pass


def run_command(arguments, cwd, env=None):
    return subprocess.run(arguments, cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=45)


def launcher_env():
    env = os.environ.copy()
    env.pop('PREVIOUS_VERSION', None)
    env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env['PATH']
    return env


def test_launcher_from_other_directory(package, repository, tmp_path):
    result = run_command(['bash', str(repository / 'tools/verify.sh')], tmp_path, launcher_env())
    assert result.returncode == 0, result.stderr
    assert expected_pass(package) in result.stdout


@pytest.mark.parametrize('arguments,message', [(['--unknown'], 'Usage:'), ([], 'Invalid VERSION')])
def test_launcher_failure(package, repository, arguments, message):
    if not arguments:
        (package / 'VERSION').write_text('bad-version')
    result = run_command(['bash', 'tools/verify.sh', *arguments], repository, launcher_env())
    assert result.returncode != 0
    assert message in result.stderr
    assert 'PASS:' not in result.stdout


def test_optimized_python_cannot_bypass_validation(package, repository):
    (package / 'CONTENT.json').write_text('{}')
    code = 'import sys;sys.path.insert(0,"tools");from verify import main;raise SystemExit(main([]))'
    result = run_command([sys.executable, '-O', '-I', '-c', code], repository, launcher_env())
    assert result.returncode == 1
    assert 'Content lock drift' in result.stderr


def test_shell_selftest(repository):
    result = run_command(['bash', 'tools/verify.sh', '--self-test'], repository, launcher_env())
    assert result.returncode == 0, result.stderr
    assert result.stdout.count('SELFTEST:') == 10
