# Location: tests/test_archive.py
# Purpose: exercise exact runtime ZIP census, safety and source-byte checks.
# Functions: real archive controls and individual corruptions.
# Calls: archive_checks and real temporary Git repositories.
# Imports: json, stat, zipfile, pytest, archive_checks, conftest.
import copy
import json
import stat
import zipfile
import pytest
import archive_checks as checks
from conftest import archive_candidate


def rewrite_archive(path, transform):
    with zipfile.ZipFile(path) as archive:
        entries = [(info, archive.read(info)) for info in archive.infolist()]
        comment = archive.comment
    with zipfile.ZipFile(path, 'w') as archive:
        archive.comment = comment
        for info, body in transform(entries):
            archive.writestr(copy.copy(info), body)


def test_actual_archive_validates_outside_package(candidate, tmp_path):
    path, sha = archive_candidate(candidate, tmp_path)
    assert 'clean archive: 38 runtime files' in checks.validate_archive(path, candidate, sha)
    assert 'clean archive: 38 runtime files' in checks.validate_archive(path, candidate)
    with zipfile.ZipFile(path) as archive:
        assert 'tools/release_checks.py' not in archive.namelist()
        assert 'AGENTS.md' not in archive.namelist()
        assert '.gitattributes' not in archive.namelist()
        assert len([info for info in archive.infolist() if not info.is_dir()]) == 38


def test_prefixed_archive(candidate, tmp_path):
    path, sha = archive_candidate(candidate, tmp_path, 'convertia-release/')
    assert 'clean archive: 38 runtime files' in checks.validate_archive(path, candidate, sha, 'convertia-release')
    with pytest.raises(ValueError, match='Unexpected archive prefix'):
        checks.validate_archive(path, candidate, sha, 'other')


@pytest.mark.parametrize('name', ['../escape', '/absolute', 'a//b', 'a/./b', 'a/../b',
                                  'C:drive', 'a\\b', '', 'nul\x00'])
def test_unsafe_paths(name):
    with pytest.raises(ValueError, match='Unsafe archive path'):
        checks.safe_path(name)


@pytest.mark.parametrize('mutation,diagnostic', [
    ('missing', 'Archive census mismatch'), ('extra', 'Unexpected archive file'),
    ('duplicate', 'Duplicate archive entry'), ('corrupt', 'Archive bytes differ'),
    ('short', 'Archive bytes differ'), ('symlink', 'Unsafe archive mode'),
    ('execute', 'Unsafe archive mode'), ('fifo', 'Unsafe archive mode'),
    ('directory-payload', 'Unexpected directory payload'),
    ('directory-symlink', 'Unsafe directory mode'), ('extra-directory', 'Unexpected archive directory'),
    ('traversal', 'Unsafe archive path'), ('null', 'Unsafe archive path'),
    ('double-slash-directory', 'Unsafe archive path')])
def test_archive_rejects_whole_output(candidate, tmp_path, mutation, diagnostic):
    path, sha = archive_candidate(candidate, tmp_path)
    def mutate(entries):
        chosen = next(pair for pair in entries if pair[0].filename == 'LICENSE')
        if mutation == 'missing':
            entries.remove(chosen)
        elif mutation == 'duplicate':
            entries.append(chosen)
        elif mutation in {'corrupt', 'short'}:
            entries[entries.index(chosen)] = (chosen[0], b'x' * (len(chosen[1]) if mutation == 'corrupt' else 2))
        elif mutation in {'symlink', 'execute', 'fifo'}:
            mode = {'symlink': stat.S_IFLNK | 0o644, 'execute': stat.S_IFREG | 0o755, 'fifo': stat.S_IFIFO | 0o644}
            chosen[0].external_attr = mode[mutation] << 16
        elif mutation == 'directory-payload':
            index = next(index for index, (info, _) in enumerate(entries) if info.is_dir())
            entries[index] = (entries[index][0], b'hidden payload')
        elif mutation == 'directory-symlink':
            next(info for info, _ in entries if info.is_dir()).external_attr = (stat.S_IFLNK | 0o755) << 16
        else:
            name = {'extra': 'tools/injected.py', 'extra-directory': 'unexpected/',
                    'traversal': '../outside', 'null': 'nullX', 'double-slash-directory': 'skills//'}[mutation]
            entries.append((zipfile.ZipInfo(name), b''))
        return entries
    rewrite_archive(path, mutate)
    if mutation == 'null':
        path.write_bytes(path.read_bytes().replace(b'nullX', b'null\x00'))
    with pytest.raises(ValueError, match=diagnostic):
        checks.validate_archive(path, candidate, sha)


def test_archive_commit_provenance(candidate, tmp_path):
    path, sha = archive_candidate(candidate, tmp_path)
    with zipfile.ZipFile(path, 'a') as archive:
        archive.comment = b'wrong commit'
    with pytest.raises(ValueError, match='Archive commit provenance mismatch'):
        checks.validate_archive(path, candidate, sha)


def test_archive_uses_committed_bytes(candidate, tmp_path):
    path, sha = archive_candidate(candidate, tmp_path)
    (candidate / 'LICENSE').write_text('uncommitted corruption')
    assert 'clean archive: 38' in checks.validate_archive(path, candidate, sha)
    with pytest.raises(ValueError, match='Archive bytes differ'):
        checks.validate_archive(path, candidate)


@pytest.mark.parametrize('lock,diagnostic', [([], 'Expected 29'), ({}, 'Expected 29'),
    ({f'skills/a{i}.py': 'x' for i in range(29)}, 'Invalid runtime skill'),
    ({f'outside/a{i}.md': 'x' for i in range(29)}, 'Invalid runtime skill')])
def test_invalid_runtime_lock(lock, diagnostic):
    with pytest.raises(ValueError, match=diagnostic):
        checks.runtime_paths(lock)


@pytest.mark.parametrize('mutation,diagnostic', [('symlink', 'Source symlink'), ('execute', 'Unsafe source mode')])
def test_unsafe_source(package, mutation, diagnostic):
    path = package / 'LICENSE'
    if mutation == 'symlink':
        path.unlink()
        path.symlink_to(package / 'README.md')
    else:
        path.chmod(0o755)
    with pytest.raises(ValueError, match=diagnostic):
        checks.source_files(package, None)


def test_missing_source_file(package):
    (package / 'LICENSE').unlink()
    with pytest.raises(FileNotFoundError):
        checks.source_files(package, None)


def test_malformed_archive_cli(candidate, tmp_path, capsys):
    path = tmp_path / 'bad.zip'
    path.write_bytes(b'not a ZIP')
    sha = checks.git_read(candidate, 'rev-parse', 'HEAD').decode().strip()
    assert checks.main([str(path), str(candidate), sha]) == 1
    assert 'FAIL: File is not a zip file' in capsys.readouterr().err


def test_cli_success_and_usage(candidate, tmp_path, monkeypatch, capsys):
    path, sha = archive_candidate(candidate, tmp_path)
    monkeypatch.setattr(checks.sys, 'argv', ['verify-archive', str(path), str(candidate), sha])
    assert checks.main() == 0
    assert 'clean archive: 38' in capsys.readouterr().out
    assert checks.main([]) == 1
    assert 'Usage:' in capsys.readouterr().err


def test_bad_commit(candidate):
    with pytest.raises(ValueError, match='Expected exact'):
        checks.source_files(candidate, 'HEAD')
