# Location: tools/repository_checks.py
# Purpose: enforce published repository restrictions before candidate distribution.
# Functions: filename, attribute, inventory, size and repository checks.
# Calls: Git read-only inventory and existing package validation.
# Imports: io, re, stat, unicodedata, zipfile, pathlib, archive_checks, release_checks, repo_layout, asset_checks.
import io
import re
import stat
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath
from archive_checks import git_read, runtime_paths, safe_path
from release_checks import read_json, require, validate
from repo_layout import PLUGIN_PATH, plugin_root
from asset_checks import check_runtime_asset

MAX_ENTRIES = 10_000
MAX_UNPACKED = 256 * 1024 * 1024
MAX_ARCHIVE = 50 * 1024 * 1024
MAX_PLUGIN_FILE = 5 * 1024 * 1024
MAX_TEXT_FILE = 256 * 1024
REWRITING = {'export-ignore', 'export-subst', 'filter', 'working-tree-encoding',
             'ident', 'text', 'eol', 'crlf'}
DEVICES = {'con', 'prn', 'aux', 'nul', 'conin$', 'conout$'} | {
    stem + digit for stem in ('com', 'lpt') for digit in '123456789¹²³'}
SYSTEM_FILES = {'.ds_store', 'thumbs.db', 'desktop.ini', '__macosx'}


def check_name(name):
    safe_path(name)
    for part in name.split('/'):
        require(not re.search(r'[<>"|?*\x00-\x1f]', part) and not part.endswith((' ', '.')),
                f'Unsafe cross-platform name: {name}')
        require(part.split('.')[0].casefold() not in DEVICES, f'Reserved device name: {name}')
        require(part.casefold() not in SYSTEM_FILES, f'OS metadata file: {name}')


def check_attributes(name, body):
    if PurePosixPath(name).name == '.gitattributes':
        for line in body.decode('utf-8').splitlines():
            if line.strip() and not line.lstrip().startswith('#'):
                attributes = {token.lstrip('-!').split('=')[0] for token in line.split()[1:]}
                require(not attributes & REWRITING, f'Forbidden rewriting attributes: {name}')


def check_limits(entries):
    names = set(entries)
    names.update(str(parent) for name in entries for parent in PurePosixPath(name).parents
                 if str(parent) != '.')
    require(len(names) < MAX_ENTRIES, 'Repository file/folder count limit exceeded')
    require(sum(map(len, entries.values())) < MAX_UNPACKED, 'Repository unpacked size limit exceeded')
    with io.BytesIO() as output:
        with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, body in entries.items():
                archive.writestr(name, body)
        require(output.tell() < MAX_ARCHIVE, 'Repository archive size limit exceeded')


def check_inventory(entries, plugin_prefix):
    seen = {}
    for name, body in entries.items():
        check_name(name)
        for path in [name, *(str(parent) for parent in PurePosixPath(name).parents if str(parent) != '.')]:
            folded = unicodedata.normalize('NFC', path).casefold()
            require(folded not in seen or seen[folded] == path, f'Case-colliding paths: {path}')
            seen[folded] = path
        check_attributes(name, body)
        require(not body.startswith(b'version https://git-lfs.github.com/spec/v1'), f'Git LFS pointer: {name}')
        if name.startswith(plugin_prefix):
            require(len(body) < MAX_PLUGIN_FILE, f'Plugin file exceeds 5 MiB: {name}')
            if not name.endswith('.png'):
                require(len(body) < MAX_TEXT_FILE, f'Plugin text exceeds review limit: {name}')
            check_runtime_asset(name, body)
    check_limits(entries)


def repository_files(root):
    modes = git_read(root, 'ls-files', '--stage', '-z').decode().split('\0')
    for entry in filter(None, modes):
        mode, name = entry.split(' ', 1)[0], entry.split('\t', 1)[1]
        require(mode in {'100644', '100755'}, f'Nonregular tracked entry: {name}')
    names = git_read(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').decode().split('\0')
    entries = {}
    for name in sorted(set(names) - {''}):
        path = root / name
        require(path.exists() or path.is_symlink(), f'Missing repository entry: {name}')
        require(stat.S_ISREG(path.lstat().st_mode), f'Nonregular repository entry: {name}')
        entries[name] = path.read_bytes()
    return entries


def validate_repository(root):
    root = Path(root).resolve()
    plugin = plugin_root(root)
    require(plugin == root / PLUGIN_PATH, 'Expected canonical plugins/convertia directory')
    entries = repository_files(root)
    check_inventory(entries, PLUGIN_PATH + '/')
    expected = runtime_paths(read_json(plugin / 'CONTENT.json'))
    actual = {path.relative_to(plugin).as_posix() for path in plugin.rglob('*') if path.is_file()}
    require(len(actual) <= 512, 'Plugin file count exceeds 512')
    require(actual == expected, 'Plugin census mismatch: unexpected or missing runtime file')
    require(not (root / 'plugin.json').exists(), 'Legacy root plugin must be relocated')
    market = read_json(root / '.claude-plugin/marketplace.json')
    canonical = read_json(plugin / 'plugin.json')
    require(market.get('plugins') == [{'name': 'convertia', 'source': './' + PLUGIN_PATH,
                                    'description': canonical['description']}], 'Repository marketplace drift')
    prose = re.sub(r'```.*?```', '', (plugin / 'README.md').read_text(), flags=re.S)
    require(len(prose.split()) >= 40, 'Plugin README below 40 words')
    return validate(plugin) + '; repository policy passed'
