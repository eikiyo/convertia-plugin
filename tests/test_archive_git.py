# Location: tests/test_archive_git.py
# Purpose: prove export rules on real Git archives and the external CLI.
# Functions: commit_candidate and tracked-source/export mutation tests.
# Calls: temporary Git repositories and archive_checks.
# Imports: os, subprocess, sys, zipfile, pathlib, pytest, conftest, archive_checks.
import os
import subprocess
import sys
import zipfile
from pathlib import Path
import pytest
import archive_checks as checks
from conftest import archive_candidate


def commit_candidate(root):
    checks.git_read(root, 'add', '-f', '.')
    checks.git_read(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                    '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                    'commit', '-qm', 'mutation fixture')


@pytest.mark.parametrize('name', ['unknown.txt', 'new/deep/unknown.py', 'skills/convertia/unknown.md',
                                 '.claude-plugin/icon.png.bak', '.claude-plugin/unknown.json'])
def test_default_exclusion_covers_new_tracked_files(candidate, tmp_path, name):
    file = candidate / name
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text('unapproved runtime file')
    commit_candidate(candidate)
    archive, sha = archive_candidate(candidate, tmp_path)
    assert 'clean archive: 38' in checks.validate_archive(archive, candidate, sha)
    with zipfile.ZipFile(archive) as package:
        assert name not in package.namelist()


@pytest.mark.parametrize('attributes,diagnostic', [
    ('/tools -export-ignore\n/tools/release_checks.py -export-ignore\n', 'Unexpected archive directory'),
    ('/README.md export-ignore\n', 'Archive census mismatch'),
    ('/unknown.txt -export-ignore\n', 'Unexpected archive file')])
def test_real_export_attribute_corruptions(candidate, tmp_path, attributes, diagnostic):
    (candidate / 'unknown.txt').write_text('unknown developer content')
    with (candidate / '.gitattributes').open('a') as output:
        output.write(attributes)
    commit_candidate(candidate)
    archive, sha = archive_candidate(candidate, tmp_path)
    with pytest.raises(ValueError, match=diagnostic):
        checks.validate_archive(archive, candidate, sha)


def test_committed_runtime_corruption(candidate, tmp_path):
    (candidate / 'VERSION').write_text('invalid')
    commit_candidate(candidate)
    archive, sha = archive_candidate(candidate, tmp_path)
    with pytest.raises(ValueError, match='Invalid VERSION'):
        checks.validate_archive(archive, candidate, sha)


def test_committed_executable_rejected(candidate, tmp_path):
    checks.git_read(candidate, 'update-index', '--chmod=+x', 'LICENSE')
    checks.git_read(candidate, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                    '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                    'commit', '-qm', 'executable fixture')
    archive, sha = archive_candidate(candidate, tmp_path)
    with pytest.raises(ValueError, match='Unsafe source mode: LICENSE'):
        checks.validate_archive(archive, candidate, sha)


def test_annotated_tag_object_is_not_a_commit(candidate):
    checks.git_read(candidate, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                    '-c', 'tag.gpgsign=false', 'tag', '-am', 'annotated fixture', 'fixture')
    tag = checks.git_read(candidate, 'rev-parse', 'fixture').decode().strip()
    with pytest.raises(ValueError, match='Expected a commit'):
        checks.source_files(candidate, tag)


def test_archive_launcher_from_outside(candidate, tmp_path):
    archive, sha = archive_candidate(candidate, tmp_path)
    env = os.environ.copy()
    env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env['PATH']
    command = ['bash', str(candidate / 'tools/verify-archive.sh'), str(archive), str(candidate), sha]
    result = subprocess.run(command, cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert 'clean archive: 38' in result.stdout
    result = subprocess.run(command[:-1], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 1
    assert 'Usage:' in result.stderr
