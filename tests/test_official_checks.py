# Location: tests/test_official_checks.py
# Purpose: validate the official schema and all expected skill entrypoints.
# Functions: official validation positive and negative controls.
# Calls: official_checks.validate_official against isolated candidate files.
# Imports: json, pytest, jsonschema, official_checks.
import json
import pytest
from jsonschema import ValidationError
import official_checks as checks


def test_official_validation_accepts_package(package):
    assert checks.validate_official(package) == (
        'PASS: official portable schema and all nine Agent Skills entrypoints')


@pytest.mark.parametrize('mutation', ['extra', 'missing'])
def test_official_skill_entrypoint_census(package, mutation):
    source = package / 'skills/customer/SKILL.md'
    if mutation == 'extra':
        target = package / 'skills/unknown/SKILL.md'
        target.parent.mkdir()
        target.write_bytes(source.read_bytes())
    else:
        source.rename(source.with_name('MISSING.md'))
    with pytest.raises(ValueError, match='Official skill entrypoint census mismatch'):
        checks.validate_official(package)


def test_official_skill_name_must_match_directory(package):
    source = package / 'skills/customer/SKILL.md'
    source.write_text(source.read_text().replace('name: customer', 'name: bad', 1))
    with pytest.raises(ValueError, match='Official skill validation failed'):
        checks.validate_official(package)


def test_portable_plugin_name_must_be_string(package):
    manifest = package / 'plugin.json'
    data = json.loads(manifest.read_text())
    data['name'] = 42
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValidationError):
        checks.validate_official(package)


def test_official_schema_hash_is_pinned(package, tmp_path, monkeypatch):
    schema = tmp_path / 'plugin.schema.json'
    schema.write_bytes(checks.SCHEMA.read_bytes() + b'\n')
    monkeypatch.setattr(checks, 'SCHEMA', schema)
    with pytest.raises(ValueError, match='Official schema hash drift'):
        checks.validate_official(package)
