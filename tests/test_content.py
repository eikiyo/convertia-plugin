# Location: tests/test_content.py
# Purpose: exercise content integrity and forbidden dependency failures.
# Functions: lock, question identifier, PDF and MCP mutation tests.
# Calls: real release validator.
# Imports: re, pytest, conftest, release_checks.
import re
import pytest
from conftest import refresh_lock
from release_checks import validate


def test_changed_content(package):
    path = package / 'skills/customer/SKILL.md'
    path.write_text(path.read_text() + '\nChanged body\n')
    with pytest.raises(ValueError, match='Content lock drift'):
        validate(package)


def test_missing_reference(package):
    path = package / 'skills/convertia/references/project-context.md'
    path.unlink()
    refresh_lock(package)
    with pytest.raises(ValueError, match='Missing or external skill reference'):
        validate(package)


@pytest.mark.parametrize('kind', ['removed', 'duplicate'])
def test_question_ids(package, kind):
    paths = list((package / 'skills/convertia/references/fundamentals').rglob('*.md'))
    path = next(path for path in paths if len(re.findall(r'^- [A-Z][A-Z0-9-]*-[A-Z]*\d+:', path.read_text(), re.M)) > 1)
    body = path.read_text()
    ids = re.findall(r'^- ([A-Z][A-Z0-9-]*-[A-Z]*\d+):', body, re.M)
    replacement = '' if kind == 'removed' else f'- {ids[1]}:'
    path.write_text(body.replace(f'- {ids[0]}:', replacement, 1))
    refresh_lock(package)
    with pytest.raises(ValueError, match='Question IDs:'):
        validate(package)


def test_pdf(package):
    (package / 'skills/private.pdf').write_bytes(b'%PDF-1.7')
    refresh_lock(package)
    with pytest.raises(ValueError, match='Private PDF included'):
        validate(package)


def test_mcp(package):
    (package / '.mcp.json').write_text('{}')
    with pytest.raises(ValueError, match='Unexpected MCP dependency'):
        validate(package)
