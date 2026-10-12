# Location: tests/test_e2e.py
# Purpose: verify real shell execution and candidate Git archive boundaries.
# Functions: run_command, launcher tests, archived candidate tests.
# Calls: bash, Python and git with temporary repository only.
# Imports: os, subprocess, sys, zipfile, pytest.
import os
import subprocess
import sys
import zipfile
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


def test_launcher_from_other_directory(package, tmp_path):
    result = run_command(['bash', str(package / 'tools/verify.sh')], tmp_path, launcher_env())
    assert result.returncode == 0, result.stderr
    assert expected_pass(package) in result.stdout


@pytest.mark.parametrize('arguments,message', [(['--unknown'], 'Usage:'), ([], 'Invalid VERSION')])
def test_launcher_failure(package, arguments, message):
    if not arguments:
        (package / 'VERSION').write_text('bad-version')
    result = run_command(['bash', 'tools/verify.sh', *arguments], package, launcher_env())
    assert result.returncode != 0
    assert message in result.stderr
    assert 'PASS:' not in result.stdout


def test_optimized_python_cannot_bypass_validation(package):
    (package / 'CONTENT.json').write_text('{}')
    code = 'import sys;sys.path.insert(0,"tools");from verify import main;raise SystemExit(main([]))'
    result = run_command([sys.executable, '-O', '-I', '-c', code], package, launcher_env())
    assert result.returncode == 1
    assert 'Content lock drift' in result.stderr


def test_shell_selftest(package):
    result = run_command(['bash', 'tools/verify.sh', '--self-test'], package, launcher_env())
    assert result.returncode == 0, result.stderr
    assert result.stdout.count('SELFTEST:') == 10


def assert_release_archive(names):
    assert not any(name.endswith('.bak') for name in names), 'Backup included in archive'
    assert not any(name.startswith('.venv') for name in names), 'Environment included in archive'
    assert 'tools/release_checks.py' in names


@pytest.mark.parametrize('tracked_backup', [False, True])
def test_candidate_git_archive(package, tmp_path, tracked_backup):
    # Commit current candidate bytes in an isolated repository, never stale checkout HEAD.
    if tracked_backup:
        (package / '.claude-plugin/icon.png.bak').write_bytes(b'forbidden backup')
    inventory = [str(path.relative_to(package)) for path in package.rglob('*') if path.is_file()]
    for command in [['git', 'init', '-q'], ['git', 'add', '-f', '--', *inventory],
                    ['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                     '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                     'commit', '-qm', 'candidate fixture']]:
        result = run_command(command, package)
        assert result.returncode == 0, result.stderr
    archive = tmp_path / 'candidate.zip'
    result = run_command(['git', 'archive', '--format=zip', f'--output={archive}', 'HEAD'], package)
    assert result.returncode == 0, result.stderr
    target = tmp_path / 'unpacked'
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        if tracked_backup:
            with pytest.raises(AssertionError, match='Backup included in archive'):
                assert_release_archive(names)
            return
        assert_release_archive(names)
        zipped.extractall(target)
    result = run_command(['bash', 'tools/verify.sh'], target, launcher_env())
    assert result.returncode == 0, result.stderr
    assert expected_pass(package) in result.stdout
