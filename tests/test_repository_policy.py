# Location: tests/test_repository_policy.py
# Purpose: enforce the supplied repository publication policy with real inputs.
# Functions: filename, attribute, inventory, limit, Git and repository tests.
# Calls: repository_checks and temporary Git indexes.
# Imports: io, json, subprocess, zipfile, pytest, repository_checks.
import io
import json
import subprocess
import zipfile

import pytest
import repository_checks as checks


def git(root, *args, data=None):
    return subprocess.run(['git', *args], cwd=root, input=data, check=True,
                          capture_output=True, timeout=30).stdout.decode().strip()


def test_valid_name():
    assert checks.check_name('skills/customer/SKILL.md') is None


@pytest.mark.parametrize('name,diagnostic', [
    ('skills/a:b', 'Unsafe archive path'),
    ('skills/a<b', 'Unsafe cross-platform name'),
    ('skills/name.', 'Unsafe cross-platform name'),
    ('skills/name ', 'Unsafe cross-platform name'),
    *[(name, 'Reserved device name') for name in
      ['con.md', 'PRN', 'com1.txt', 'LPT9', 'NUL']],
])
def test_rejected_names(name, diagnostic):
    with pytest.raises(ValueError, match=diagnostic):
        checks.check_name(name)


@pytest.mark.parametrize('component', ['.DS_Store', 'Thumbs.db', 'desktop.ini', '__MACOSX'])
@pytest.mark.parametrize('template', ['{}', 'skills/{}/data.md', 'skills/{}'])
def test_system_components(component, template):
    with pytest.raises(ValueError, match='OS metadata file'):
        checks.check_name(template.format(component))


@pytest.mark.parametrize('name,body', [
    ('.gitattributes', b'*.png binary\n'),
    ('nested/.gitattributes', b'\n  \n# * export-ignore\n  # * filter=lfs\n'),
    ('README.md', b'* export-ignore\n'),
])
def test_allowed_attributes(name, body):
    assert checks.check_attributes(name, body) is None


@pytest.mark.parametrize('attribute', [
    'export-ignore', 'export-subst', 'filter', 'working-tree-encoding',
    'ident', 'text', 'eol', 'crlf', '-export-ignore', '!filter', 'filter=lfs',
])
@pytest.mark.parametrize('name', ['.gitattributes', 'nested/.gitattributes'])
def test_rewriting_attributes(name, attribute):
    with pytest.raises(ValueError, match='Forbidden rewriting attributes'):
        checks.check_attributes(name, f'* {attribute}\n'.encode())


def test_valid_inventory():
    assert checks.check_inventory({'plugins/convertia/README.md': b'normal'},
                                  'plugins/convertia/') is None


@pytest.mark.parametrize('entries', [
    {'README.md': b'a', 'readme.md': b'b'},
    {'Skills/a.md': b'a', 'skills/b.md': b'b'},
    {'caf\u00e9.md': b'a', 'cafe\u0301.md': b'b'},
])
def test_inventory_aliases(entries):
    with pytest.raises(ValueError, match='Case-colliding paths'):
        checks.check_inventory(entries, 'plugins/convertia/')


def test_inventory_lfs_pointer():
    with pytest.raises(ValueError, match='Git LFS pointer'):
        checks.check_inventory({'file': b'version https://git-lfs.github.com/spec/v1\n'},
                               'plugins/convertia/')


@pytest.mark.parametrize('name,constant,diagnostic', [
    ('image.png', 'MAX_PLUGIN_FILE', 'Plugin file exceeds 5 MiB'),
    ('README.md', 'MAX_TEXT_FILE', 'Plugin text exceeds review limit'),
])
def test_plugin_file_boundaries(monkeypatch, package, name, constant, diagnostic):
    body = (package / '.claude-plugin/icon.png').read_bytes() if name.endswith('.png') else b'normal text'
    monkeypatch.setattr(checks, constant, len(body) + 1)
    path = 'plugins/convertia/' + name
    assert checks.check_inventory({path: body}, 'plugins/convertia/') is None
    monkeypatch.setattr(checks, constant, len(body))
    with pytest.raises(ValueError, match=diagnostic):
        checks.check_inventory({path: body}, 'plugins/convertia/')


def test_png_exempt_from_text_limit(monkeypatch, package):
    monkeypatch.setattr(checks, 'MAX_TEXT_FILE', 8)
    assert checks.check_inventory({'plugins/convertia/icon.png': (package / '.claude-plugin/icon.png').read_bytes()},
                                  'plugins/convertia/') is None


def test_external_file_exempt_from_plugin_limits(monkeypatch):
    monkeypatch.setattr(checks, 'MAX_PLUGIN_FILE', 8)
    monkeypatch.setattr(checks, 'MAX_TEXT_FILE', 8)
    assert checks.check_inventory({'README.md': b'x' * 8}, 'plugins/convertia/') is None


def test_count_limit_includes_directories(monkeypatch):
    monkeypatch.setattr(checks, 'MAX_ENTRIES', 3)
    assert checks.check_limits({'one/file': b'a'}) is None
    with pytest.raises(ValueError, match='Repository file/folder count limit exceeded'):
        checks.check_limits({'one/two/file': b'a'})


def test_unpacked_limit(monkeypatch):
    monkeypatch.setattr(checks, 'MAX_UNPACKED', 8)
    assert checks.check_limits({'a': b'123', 'b': b'4567'}) is None
    with pytest.raises(ValueError, match='Repository unpacked size limit exceeded'):
        checks.check_limits({'a': b'1234', 'b': b'5678'})


def test_archive_limit(monkeypatch):
    entries = {'a': b'payload'}
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('a', entries['a'])
        size = buffer.tell()
    monkeypatch.setattr(checks, 'MAX_ARCHIVE', size + 1)
    assert checks.check_limits(entries) is None
    monkeypatch.setattr(checks, 'MAX_ARCHIVE', size)
    with pytest.raises(ValueError, match='Repository archive size limit exceeded'):
        checks.check_limits(entries)


def test_repository_files_regular_entries(tmp_path):
    git(tmp_path, 'init', '-q')
    (tmp_path / 'tracked').write_bytes(b'tracked data')
    (tmp_path / 'other').write_bytes(b'untracked data')
    git(tmp_path, 'add', 'tracked')
    assert checks.repository_files(tmp_path) == {
        'tracked': b'tracked data', 'other': b'untracked data'}


@pytest.mark.parametrize('tracked', [False, True])
def test_repository_files_symlink(tmp_path, tracked):
    git(tmp_path, 'init', '-q')
    (tmp_path / 'link').symlink_to('absent-target')
    if tracked:
        git(tmp_path, 'add', 'link')
    diagnostic = 'Nonregular tracked entry' if tracked else 'Nonregular repository entry'
    with pytest.raises(ValueError, match=diagnostic):
        checks.repository_files(tmp_path)


def test_repository_files_submodule_mode(tmp_path):
    git(tmp_path, 'init', '-q')
    tree = git(tmp_path, 'mktree', data=b'')
    commit = git(tmp_path, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 'commit-tree', tree, data=b'fixture\n')
    git(tmp_path, 'update-index', '--add', '--cacheinfo', f'160000,{commit},module')
    with pytest.raises(ValueError, match='Nonregular tracked entry'):
        checks.repository_files(tmp_path)


def test_repository_files_missing_index_entry(tmp_path):
    git(tmp_path, 'init', '-q')
    blob = git(tmp_path, 'hash-object', '-w', '--stdin', data=b'missing')
    git(tmp_path, 'update-index', '--add', '--cacheinfo', f'100644,{blob},missing')
    with pytest.raises(ValueError, match='Missing repository entry'):
        checks.repository_files(tmp_path)


def test_valid_repository(repository, candidate):
    assert 'repository policy passed' in checks.validate_repository(repository)


def test_missing_canonical_plugin(tmp_path):
    with pytest.raises(ValueError, match='Expected canonical plugins/convertia directory'):
        checks.validate_repository(tmp_path)


def test_extra_plugin_file(repository, candidate):
    (candidate / 'extra.txt').write_text('extra')
    with pytest.raises(ValueError, match='Plugin census mismatch'):
        checks.validate_repository(repository)


def test_missing_runtime_file(repository, candidate):
    (candidate / 'README.md').rename(repository / 'moved-readme.md')
    git(repository, 'update-index', '--force-remove', 'plugins/convertia/README.md')
    with pytest.raises(ValueError, match='Plugin census mismatch'):
        checks.validate_repository(repository)


def test_legacy_root_plugin(repository, candidate):
    (repository / 'plugin.json').write_text('{}')
    with pytest.raises(ValueError, match='Legacy root plugin must be relocated'):
        checks.validate_repository(repository)


def test_marketplace_source_drift(repository, candidate):
    path = repository / '.claude-plugin/marketplace.json'
    market = json.loads(path.read_text())
    market['plugins'][0]['source'] = './wrong'
    path.write_text(json.dumps(market))
    with pytest.raises(ValueError, match='Repository marketplace drift'):
        checks.validate_repository(repository)


def test_readme_excludes_fenced_code(repository, candidate):
    (candidate / 'README.md').write_text(' '.join(['word'] * 39) +
                                        '\n```text\n' + ' '.join(['code'] * 80) + '\n```\n')
    with pytest.raises(ValueError, match='Plugin README below 40 words'):
        checks.validate_repository(repository)


def test_plugin_file_count(repository, candidate):
    current = sum(path.is_file() for path in candidate.rglob('*'))
    for index in range(513 - current):
        (candidate / f'extra-{index}.txt').write_text('extra')
    with pytest.raises(ValueError, match='Plugin file count exceeds 512'):
        checks.validate_repository(repository)
