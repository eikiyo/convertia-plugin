# Location: tests/test_content_contracts.py
# Purpose: prove instruction contract controls reject each targeted regression.
# Functions: real control, clause deletion, blanket-ban and legacy identifier tests.
# Calls: actual release validator with independently refreshed fixture locks.
# Imports: pytest, conftest, content_contracts, release_checks.
import pytest
from conftest import refresh_lock, expected_pass
from content_contracts import REQUIRED, NORMATIVE, RESPONSE, LANGUAGE, contract_errors
from release_checks import validate

CLAUSES = [(name, clause) for name, clauses in REQUIRED.items() for clause in clauses]
BANS = [
    'Use ordinary chat text with Markdown only.',
    'Text is the intended output, not a fallback.',
    'Never create artifacts.',
    'Do not use native artifacts.',
    'Never generate cards, banners, HTML, widgets, fake expanders or a separate viewer.',
    'Never call a renderer, MCP display tool or app.',
    'No renderer tools, app windows, HTML, cards, banners, expanders or decorative dashboards.',
]


def test_real_runtime_contract(package):
    assert contract_errors(package) == []
    assert validate(package) == expected_pass(package)


def test_unavailable_scope_rule_cannot_be_replaced_by_unverified_host_claim(package):
    target = package / RESPONSE
    clause = ("Scope capability limits to this session's exposed tools and permissions. "
              'Do not claim that an entire host lacks artifact support or guarantee that '
              'switching hosts or accounts will succeed without verified availability.')
    assert clause in target.read_text()
    target.write_text(target.read_text().replace(
        clause, 'Claude Code cannot create artifacts; another host will produce one.'))
    refresh_lock(package)
    assert contract_errors(package) == [f'Missing instruction contract: {RESPONSE}: {clause}']
    with pytest.raises(ValueError, match='Missing instruction contract:.*Scope capability limits'):
        validate(package)


@pytest.mark.parametrize('clause,replacement', [
    ('Swedish must be the complete counterpart of English, not a summary.',
     'Swedish may summarize the English definition and example.'),
    ('Every material definition, example, contract issue, qualification, warning and next action must appear in both language blocks.',
     'Keep the 10000 SEK fee, 200000 SEK spending and reliance caveats in English only.'),
    ('Shorten both versions together; never save space by dropping Swedish propositions.',
     'Save space by shortening only the Swedish qualifications.'),
    ('Keep all substantive prose inside the two language blocks.',
     'Put a shared English warning after the two language blocks.'),
    ('Do not append an English-only or Swedish-only caveat, recommendation or conclusion.',
     'Append an English-only disclaimer on enforceability.'),
])
def test_bilingual_completeness_rule_replacement_rejected(package, clause, replacement):
    target = package / LANGUAGE
    assert clause in target.read_text()
    target.write_text(target.read_text().replace(clause, replacement))
    refresh_lock(package)
    assert contract_errors(package) == [f'Missing instruction contract: {LANGUAGE}: {clause}']
    with pytest.raises(ValueError, match='Missing instruction contract:'):
        validate(package)


def test_revision_readback_cannot_be_replaced_by_chat_only_success(package):
    target = package / RESPONSE
    clause = ('Before claiming a revision is complete, read back the actual revised '
              'deliverable and verify the changed facts, dependent calculations and preserved unknowns.')
    assert clause in target.read_text()
    target.write_text(target.read_text().replace(
        clause, 'Report the revised 12000 SEK fee in chat and reuse the original 10000 SEK file link.'))
    refresh_lock(package)
    assert contract_errors(package) == [f'Missing instruction contract: {RESPONSE}: {clause}']
    with pytest.raises(ValueError, match='Missing instruction contract:.*read back the actual revised'):
        validate(package)


@pytest.mark.parametrize('name,clause', CLAUSES)
def test_each_contract_clause_has_a_precise_negative_control(package, name, clause):
    path = package / name
    assert clause in path.read_text()
    path.write_text(path.read_text().replace(clause, '[removed contract]'))
    refresh_lock(package)
    errors = contract_errors(package)
    assert errors == [f'Missing instruction contract: {name}: {clause}']
    # Removing a Markdown path would otherwise hide the result behind the link check.
    with pytest.raises(ValueError, match='Missing instruction contract:'):
        validate(package)


@pytest.mark.parametrize('name', NORMATIVE)
@pytest.mark.parametrize('ban', BANS)
def test_normative_blanket_ban_rejected(package, name, ban):
    path = package / name
    path.write_text(path.read_text() + '\n' + ban + '\n')
    refresh_lock(package)
    errors = contract_errors(package)
    assert len(errors) == 1
    assert errors[0].startswith(f'Conflicting blanket artifact ban: {name}:')
    with pytest.raises(ValueError, match='Conflicting blanket artifact ban:'):
        validate(package)


@pytest.mark.parametrize('name', ['negative-cases.md', 'interaction-examples.md'])
def test_quoted_rejected_examples_are_not_normative_bans(package, name):
    path = package / 'skills/convertia/references' / name
    path.write_text(path.read_text() + '\nRejected example: "Never create artifacts."\n')
    refresh_lock(package)
    assert validate(package) == expected_pass(package)


@pytest.mark.parametrize('path,old,new,reason', [
    ('regulation.md', 'REG-001', 'REG-999', 'Legacy question identifiers changed'),
    ('legal.md', 'LEG-001', 'LEG-999', 'Legal question identifier range changed'),
])
def test_same_count_question_renaming_rejected(package, path, old, new, reason):
    target = package / 'skills/convertia/references/fundamentals/roles' / path
    assert '- ' + old + ':' in target.read_text()
    target.write_text(target.read_text().replace('- ' + old + ':', '- ' + new + ':', 1))
    refresh_lock(package)
    with pytest.raises(ValueError, match=reason):
        validate(package)
