# Location: tests/test_units.py
# Purpose: test the actual validation functions with valid and corrupt inputs.
# Functions: frontmatter, version and JSON contract tests.
# Calls: release_checks functions directly.
# Imports: json, pytest, release_checks.
import json
import pytest
from release_checks import skill_frontmatter, version_tuple, read_json, check_version

GOOD = '---\nname: customer\ndescription: "Buyer: payment and proof."\n---\n# Customer\n'


@pytest.mark.parametrize('body', [GOOD, GOOD.replace('name: customer\ndescription: "Buyer: payment and proof."',
                                                     'description: "Buyer: payment and proof."\nname: customer')])
def test_frontmatter_valid(body):
    assert skill_frontmatter(body, 'customer', 'customer/SKILL.md') is None


@pytest.mark.parametrize('old,new,reason', [
    (GOOD, '', 'delimiters'), ('---\nname', 'bad\nname', 'delimiters'),
    ('\n---\n#', '\nmissing\n#', 'delimiters'),
    ('name: customer', 'name customer', 'unsupported key'),
    ('name: customer', 'other: customer', 'unsupported key'),
    ('description: "Buyer: payment and proof."', 'name: customer', 'duplicate'),
    ('name: customer', 'name: Customer', 'name must match'),
    ('name: customer', 'name: investor', 'name must match'),
    ('"Buyer: payment and proof."', 'Buyer: payment and proof.', 'JSON-quoted'),
    ('"Buyer: payment and proof."', '7', 'nonempty string'),
    ('"Buyer: payment and proof."', '"   "', 'nonempty string'),
])
def test_frontmatter_corruption(old, new, reason):
    with pytest.raises(ValueError, match=f'Invalid skill frontmatter:.*{reason}'):
        skill_frontmatter(GOOD.replace(old, new), 'customer', 'customer/SKILL.md')


@pytest.mark.parametrize('value', ['', '1.2', 'v1.2.3', '1.2.3-pre', 'x.2.3'])
def test_invalid_version(value):
    with pytest.raises(ValueError, match='Invalid VERSION'):
        version_tuple(value, 'VERSION')


def test_numeric_versions(package):
    (package / 'VERSION').write_text('1.10.0\n')
    assert version_tuple('1.10.0', 'VERSION') == (1, 10, 0)
    assert check_version(package, '1.9.9') == '1.10.0'
    assert check_version(package, None) == '1.10.0'
    with pytest.raises(ValueError, match='Version must increase'):
        check_version(package, '1.10.0')
    with pytest.raises(ValueError, match='Invalid PREVIOUS_VERSION'):
        check_version(package, 'garbage')


@pytest.mark.parametrize('value', ['[]', 'null', '"text"', '{}'])
def test_json_object_contract(tmp_path, value):
    path = tmp_path / 'data.json'
    path.write_text(value)
    if value == '{}':
        assert read_json(path) == {}
    else:
        with pytest.raises(ValueError, match='Expected JSON object'):
            read_json(path)


def test_invalid_json(tmp_path):
    path = tmp_path / 'data.json'
    path.write_text('{')
    with pytest.raises(json.JSONDecodeError):
        read_json(path)
