# Location: tests/conftest.py
# Purpose: independent isolated candidate package fixtures.
# Functions: package, refresh_lock.
# Calls: filesystem copy and independent SHA256 lock generation.
# Imports: hashlib, json, shutil, pathlib, pytest.
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repository(tmp_path):
    target = tmp_path / 'plugin'
    inventory = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others',
                                '--exclude-standard'], cwd=ROOT, capture_output=True,
                               check=True, timeout=30).stdout.decode().split('\0')
    for name in sorted(set(inventory) - {''}):
        source = ROOT / name
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_file():
            shutil.copy2(source, destination)
    return target


@pytest.fixture
def package(repository):
    return repository / 'plugins/convertia'


def refresh_lock(root):
    lock = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((root / 'skills').rglob('*')) if path.is_file()}
    (root / 'CONTENT.json').write_text(json.dumps(lock))


def expected_pass(root):
    version = (root / 'VERSION').read_text().strip()
    count = len(json.loads((root / 'CONTENT.json').read_text()))
    return f'PASS: {version}; {count} shared files; 918 unique questions; content lock matches'


@pytest.fixture
def candidate(package, repository):
    commands = [['git', 'init', '-q'], ['git', 'add', '-f', '.'],
                ['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                 'commit', '-qm', 'candidate fixture']]
    for command in commands:
        subprocess.run(command, cwd=repository, check=True, capture_output=True, timeout=30)
    return package


def archive_candidate(candidate, tmp_path, prefix=''):
    path = tmp_path / 'candidate.zip'
    subprocess.run(['git', 'archive', '--format=zip', f'--output={path}',
                    f'--prefix={prefix}', 'HEAD'], cwd=candidate, check=True, timeout=30)
    sha = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=candidate, check=True,
                         capture_output=True, text=True, timeout=30).stdout.strip()
    return path, sha
