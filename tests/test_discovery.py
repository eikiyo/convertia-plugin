# Location: tests/test_discovery.py
# Purpose: detect unreadable discovered entrypoints and declared resource drift.
# Functions: nested skill, reference and host metadata mutation tests.
# Calls: validator against modified real package fixtures.
# Imports: json, shutil, pytest, conftest, release_checks.
import json
import shutil
import pytest
from conftest import refresh_lock
from release_checks import validate


@pytest.mark.parametrize('nested', ['hidden/nested', 'hidden/customer'])
def test_nested_entrypoints(package, nested):
    path = package / 'skills' / nested
    path.mkdir(parents=True)
    (path / 'SKILL.md').write_text('malformed header')
    refresh_lock(package)
    with pytest.raises(ValueError, match='Nested skill entrypoint'):
        validate(package)


@pytest.mark.parametrize('reference', ['references/no-such-file.md', '../../../outside.md'])
def test_missing_or_external_reference(package, reference):
    path = package / 'skills/customer/SKILL.md'
    path.write_text(path.read_text() + f'\nRead `{reference}`.\n')
    refresh_lock(package)
    with pytest.raises(ValueError, match='Missing or external skill reference'):
        validate(package)


def test_shared_contract_absent(package):
    path = package / 'skills/customer/SKILL.md'
    path.write_text(path.read_text().replace('../convertia/SKILL.md', 'shared contract'))
    refresh_lock(package)
    with pytest.raises(ValueError, match='Shared contract link missing'):
        validate(package)


def test_declared_directory_missing(package):
    shutil.move(package / 'skills', package / 'saved-skills')
    # Metadata checks headings first; retain the heading file to reach the path check directly.
    from release_checks import check_host_metadata, read_json
    with pytest.raises(ValueError, match='Declared skills directory missing'):
        check_host_metadata(package, read_json(package / 'plugin.json'))


@pytest.mark.parametrize('key,value,reason', [
    ('skills', './missing', 'Invalid declared skills path'),
    ('interface', None, 'Missing Codex interface'),
    ('interface', {}, 'Host interface drift'),
])
def test_codex_metadata(package, key, value, reason):
    path = package / '.codex-plugin/plugin.json'
    data = json.loads(path.read_text())
    data[key] = value
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match=reason):
        validate(package)


def test_openai_interface_missing(package):
    path = package / 'plugin.json'
    data = json.loads(path.read_text())
    del data['extensions']
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='Missing OpenAI extensions object'):
        validate(package)


@pytest.mark.parametrize('level', ['extensions', 'vendor', 'interface'])
def test_null_host_objects(package, level):
    path = package / 'plugin.json'
    data = json.loads(path.read_text())
    if level == 'extensions':
        data['extensions'] = None
    elif level == 'vendor':
        data['extensions']['com.openai'] = None
    else:
        data['extensions']['com.openai']['interface'] = None
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='Missing OpenAI'):
        validate(package)


@pytest.mark.parametrize('prompts', ['text', [], [7], ['   ']])
def test_equal_but_invalid_default_prompt(package, prompts):
    root_path = package / 'plugin.json'
    codex_path = package / '.codex-plugin/plugin.json'
    root_data = json.loads(root_path.read_text())
    codex_data = json.loads(codex_path.read_text())
    root_data['extensions']['com.openai']['interface']['defaultPrompt'] = prompts
    codex_data['interface']['defaultPrompt'] = prompts
    root_path.write_text(json.dumps(root_data))
    codex_path.write_text(json.dumps(codex_data))
    with pytest.raises(ValueError, match='defaultPrompt must be'):
        validate(package)
