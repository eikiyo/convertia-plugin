# Location: tools/archive_checks.py
# Purpose: validate the complete installation ZIP against trusted source bytes.
# Functions: runtime_paths, source_files, archive_files, validate_archive, main.
# Calls: Git read-only commands and shared release validation.
# Imports: json, re, stat, struct, subprocess, sys, tempfile, zipfile, pathlib, release_checks.
import json
import re
import stat
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from release_checks import MANIFESTS, require, validate
from repo_layout import plugin_root

RUNTIME = {*MANIFESTS, '.claude-plugin/marketplace.json', '.claude-plugin/icon.png',
           'README.md', 'LICENSE', 'VERSION', 'CONTENT.json'}


def safe_path(name):
    require(bool(name) and not any(character in name for character in '\\:\x00'),
            f'Unsafe archive path: {name!r}')
    require(all(part not in {'', '.', '..'} for part in name.split('/')),
            f'Unsafe archive path: {name!r}')
    return name


def runtime_paths(lock):
    require(isinstance(lock, dict) and len(lock) == 29, 'Expected 29 locked skill files')
    for name in lock:
        safe_path(name)
        require(name.startswith('skills/') and name.endswith('.md'),
                f'Invalid runtime skill path: {name}')
    return RUNTIME | set(lock)


def git_read(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True,
                          capture_output=True, timeout=30).stdout


def check_commit(root, commit):
    require(re.fullmatch(r'[a-f0-9]{40}', commit), 'Expected exact 40-character commit SHA')
    require(git_read(root, 'rev-parse', f'{commit}^{{commit}}').decode().strip() == commit,
            'Expected a commit, not a tag object')


def source_files(root, commit):
    if commit is not None:
        check_commit(root, commit)
        prefix = git_read(root, 'rev-parse', '--show-prefix').decode().strip()
        read = lambda name: git_read(root, 'show', f'{commit}:{prefix}{name}')
        modes = {entry.split('\t')[1]: entry.split()[0] for entry in
                 git_read(root, 'ls-tree', '-r', commit).decode().splitlines()}
    else:
        read = lambda name: (root / name).read_bytes()
        modes = None
    names = runtime_paths(json.loads(read('CONTENT.json')))
    for name in names:
        if modes is not None:
            require(modes.get(name) == '100644', f'Unsafe source mode: {name}')
        else:
            path = root / name
            require(not any(item.is_symlink() for item in [path, *path.parents]),
                    f'Source symlink: {name}')
            require(stat.S_ISREG(path.stat().st_mode) and not path.stat().st_mode & 0o111,
                    f'Unsafe source mode: {name}')
    return {name: read(name) for name in names}


def check_extra(extra):
    while extra:
        require(len(extra) >= 4, 'Malformed ZIP extra field')
        kind, size = struct.unpack_from('<HH', extra)
        require(len(extra) >= 4 + size, 'Truncated ZIP extra field')
        require(kind != 0x7075, 'Unsafe Unicode ZIP path metadata')
        extra = extra[4 + size:]


def check_local_metadata(archive, info):
    check_extra(info.extra)
    archive.fp.seek(info.header_offset)
    header = archive.fp.read(30)
    require(len(header) == 30 and header[:4] == b'PK\x03\x04', 'Invalid ZIP local header')
    require(info.flag_bits in {0, 0x800} and info.compress_type in {0, 8},
            'Unsupported ZIP flags or compression')
    require(struct.unpack_from('<HH', header, 6) == (info.flag_bits, info.compress_type),
            'ZIP local encoding mismatch')
    require(struct.unpack_from('<III', header, 14) == (info.CRC, info.compress_size, info.file_size),
            'ZIP local size or CRC mismatch')
    name_size, extra_size = struct.unpack_from('<HH', header, 26)
    encoding = 'utf-8' if info.flag_bits & 0x800 else 'cp437'
    require(archive.fp.read(name_size) == info.orig_filename.encode(encoding),
            'ZIP local filename mismatch')
    extra = archive.fp.read(extra_size)
    require(len(extra) == extra_size, 'Truncated ZIP local metadata')
    check_extra(extra)
    return archive.fp.tell() + info.compress_size


def archive_files(archive, expected, prefix):
    directories = {str(parent) for name in expected for parent in PurePosixPath(name).parents
                   if str(parent) != '.'}
    files, seen, next_offset = {}, set(), 0
    for info in archive.infolist():
        end = check_local_metadata(archive, info)
        original = info.orig_filename
        require(original == info.filename, f'Unsafe archive path: {original!r}')
        safe_path(original[:-1] if info.is_dir() else original)
        require(original not in seen, f'Duplicate archive entry: {original}')
        seen.add(original)
        require(info.header_offset == next_offset, 'Unindexed ZIP local data or overlapping records')
        next_offset = end
        require(original.startswith(prefix), f'Unexpected archive prefix: {original}')
        name = original[len(prefix):]
        mode = info.external_attr >> 16
        if info.is_dir():
            require(info.file_size == 0, f'Unexpected directory payload: {original}')
            require(name.rstrip('/') in directories or bool(prefix) and name == '',
                    f'Unexpected archive directory: {original}')
            require(stat.S_IFMT(mode) in {0, stat.S_IFDIR}, f'Unsafe directory mode: {original}')
        else:
            require(stat.S_IFMT(mode) in {0, stat.S_IFREG} and not mode & 0o111,
                    f'Unsafe archive mode: {original}')
            require(name in expected, f'Unexpected archive file: {original}')
            require(info.file_size == len(expected[name]), 'Archive bytes differ from checked source')
            files[name] = archive.read(info)
    require(next_offset == archive.start_dir, 'Unindexed ZIP local data after final entry')
    require(set(files) == set(expected), f'Archive census mismatch: missing {sorted(set(expected) - set(files))}')
    require(files == expected, 'Archive bytes differ from checked source')
    return files


def validate_archive(path, source_root, commit=None, prefix=''):
    root = plugin_root(source_root).resolve()
    if prefix:
        safe_path(prefix)
        prefix += '/'
    expected = source_files(root, commit)
    with zipfile.ZipFile(path) as archive:
        if commit is not None:
            require(archive.comment == commit.encode(), 'Archive commit provenance mismatch')
        files = archive_files(archive, expected, prefix)
    with tempfile.TemporaryDirectory(prefix='convertia-check-') as temporary:
        target = Path(temporary)
        for name, body in files.items():
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(body)
        result = validate(target)
    return f'{result}; clean archive: {len(files)} runtime files'


def main(args=None):
    args = sys.argv[1:] if args is None else args
    try:
        require(len(args) in {3, 4}, 'Usage: verify-archive.sh ZIP SOURCE COMMIT [PREFIX]')
        print(validate_archive(*args))
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    return 0
