# Location: tests/test_package.py
# Purpose: mutate real package artifacts and assert precise rejection reasons.
# Functions: release, metadata, skill, lock and question mutation tests.
# Calls: actual validator and independent YAML parser.
# Imports: json, re, pytest, yaml, conftest, release_checks.
import json
import re
import pytest
import yaml
from conftest import refresh_lock, expected_pass
from release_checks import validate, MANIFESTS, SKILLS, METADATA


def test_real_package(package):
    result = validate(package)
    assert result == expected_pass(package)
    for path in (package / 'skills').glob('*/SKILL.md'):
        parsed = yaml.safe_load(path.read_text().split('---', 2)[1])
        assert parsed['name'] == path.parent.name
        assert isinstance(parsed['description'], str) and parsed['description'].strip()


@pytest.mark.parametrize('path', ['VERSION', *MANIFESTS, '.claude-plugin/marketplace.json',
                                  'README.md', 'CONTENT.json'])
def test_missing_required_file(package, path):
    (package / path).unlink()
    with pytest.raises(FileNotFoundError, match=re.escape(path.split('/')[-1])):
        validate(package)


@pytest.mark.parametrize('path', [*MANIFESTS, '.claude-plugin/marketplace.json', 'CONTENT.json'])
def test_malformed_json(package, path):
    (package / path).write_text('{')
    with pytest.raises(json.JSONDecodeError):
        validate(package)


@pytest.mark.parametrize('field', ['name', 'version', *METADATA])
def test_missing_canonical_field(package, field):
    path = package / 'plugin.json'
    data = json.loads(path.read_text())
    del data[field]
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match=f'Missing manifest field: {field}'):
        validate(package)


@pytest.mark.parametrize('path', MANIFESTS[1:])
@pytest.mark.parametrize('field', METADATA)
def test_metadata_drift(package, path, field):
    target = package / path
    data = json.loads(target.read_text())
    data[field] = 'changed'
    target.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='Metadata drift'):
        validate(package)


@pytest.mark.parametrize('path', MANIFESTS)
@pytest.mark.parametrize('field,value', [('version', '0.0.0'), ('name', 'wrong')])
def test_manifest_identity(package, path, field, value):
    target = package / path
    data = json.loads(target.read_text())
    data[field] = value
    target.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='Manifest drift'):
        validate(package)


@pytest.mark.parametrize('path', ['README.md', 'skills/convertia/SKILL.md'])
def test_heading_drift(package, path):
    target = package / path
    version = (package / 'VERSION').read_text().strip()
    target.write_text(target.read_text().replace(f'# Convertia {version}', '# Convertia 0.0.0'))
    with pytest.raises(ValueError, match='Heading drift'):
        validate(package)


def test_marketplace_drift(package):
    (package / '.claude-plugin/marketplace.json').write_text('{"plugins": []}')
    with pytest.raises(ValueError, match='Marketplace drift'):
        validate(package)


@pytest.mark.parametrize('name', sorted(SKILLS))
def test_each_skill_missing(package, name):
    (package / f'skills/{name}/SKILL.md').unlink()
    # The main skill is also required for its version heading.
    expected = FileNotFoundError if name == 'convertia' else ValueError
    with pytest.raises(expected):
        validate(package)


def test_extra_skill(package):
    path = package / 'skills/unexpected'
    path.mkdir()
    (path / 'SKILL.md').write_text('unexpected')
    with pytest.raises(ValueError, match='Skill entry drift'):
        validate(package)


def test_documented_command(package):
    path = package / 'README.md'
    path.write_text(path.read_text().replace('/convertia:finance', '/convertia:missing'))
    with pytest.raises(ValueError, match='Documented command drift'):
        validate(package)


@pytest.mark.parametrize('name', sorted(SKILLS - {'convertia'}))
def test_shared_link(package, name):
    path = package / f'skills/{name}/SKILL.md'
    path.write_text(path.read_text().replace('../convertia/SKILL.md', '../missing/SKILL.md'))
    refresh_lock(package)
    with pytest.raises(ValueError, match='Missing or external skill reference'):
        validate(package)


@pytest.mark.parametrize('name', ['customer', 'investor'])
def test_original_yaml_defects(package, name):
    path = package / f'skills/{name}/SKILL.md'
    lines = path.read_text().splitlines()
    lines[2] = 'description: ' + json.loads(lines[2].partition(': ')[2])
    path.write_text('\n'.join(lines) + '\n')
    refresh_lock(package)
    with pytest.raises(yaml.YAMLError):
        yaml.safe_load('\n'.join(lines[1:3]))
    with pytest.raises(ValueError, match='Invalid skill frontmatter:.*JSON-quoted'):
        validate(package)
