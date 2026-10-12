# Location: tests/test_ci_contract.py
# Purpose: prevent release CI from bypassing measured tests or publishing unchecked bytes.
# Functions: workflow, coverage configuration and test discipline assertions.
# Calls: local configuration and source reads only.
# Imports: ast, copy, re, tomllib, pathlib, pytest, yaml.
import ast
import copy
import json
import re
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = 'bash tools/test.sh -q'
LIVE = '.venv/bin/python -m pytest tests_live -q'
PUBLISH = "github.event_name == 'push' && github.ref == 'refs/heads/main'"


def workflow():
    return yaml.load((ROOT / '.github/workflows/verify.yml').read_text(), Loader=yaml.BaseLoader)


def assert_coverage_contract(config):
    run, report = config['tool']['coverage']['run'], config['tool']['coverage']['report']
    assert run['source'] == ['tools'] and run['branch'] is True
    assert report['fail_under'] == 100 and report['precision'] >= 2
    assert not run.get('omit') and not report.get('omit')
    assert not report.get('exclude_lines') and not report.get('exclude_also')


def assert_workflow_contract(config):
    assert set(config['jobs']) == {'verify'}
    job = config['jobs']['verify']
    assert 'if' not in job and 'continue-on-error' not in job
    steps = job['steps']
    assert not any('continue-on-error' in step for step in steps)
    coverage = next(index for index, step in enumerate(steps) if step.get('run') == COVERAGE)
    live = next(index for index, step in enumerate(steps) if step.get('run') == LIVE)
    package = next(index for index, step in enumerate(steps) if 'git archive' in step.get('run', ''))
    upload = next(index for index, step in enumerate(steps) if 'actions/upload-artifact@' in step.get('uses', ''))
    assert 'if' not in steps[coverage] and 'if' not in steps[live]
    assert coverage < live < package < upload
    assert all(index < package for index, step in enumerate(steps) if 'PREVIOUS_VERSION' in step.get('run', ''))
    assert steps[package]['if'] == PUBLISH and steps[upload]['if'] == PUBLISH
    assert 'git archive --format=zip --output=dist/convertia.zip "$GITHUB_SHA"' in steps[package]['run']
    assert 'sha256sum dist/convertia.zip > dist/convertia.zip.sha256' in steps[package]['run']
    assert steps[upload]['with']['name'] == 'convertia-${{ github.sha }}'
    assert steps[upload]['with']['if-no-files-found'] == 'error'
    assert set(steps[upload]['with']['path'].split()) == {'dist/convertia.zip', 'dist/convertia.zip.sha256'}
    assert all(re.fullmatch(r'[^@]+@[a-f0-9]{40}', step['uses']) for step in steps if 'uses' in step)


def test_current_ci_requires_every_gate_before_exact_commit_archive():
    assert_workflow_contract(workflow())


@pytest.mark.parametrize('mutation', ['conditional-live', 'ignored-failure', 'moving-ref', 'package-first'])
def test_ci_contract_rejects_bypasses(mutation):
    config = copy.deepcopy(workflow())
    steps = config['jobs']['verify']['steps']
    live = next(step for step in steps if step.get('run') == LIVE)
    package = next(step for step in steps if 'git archive' in step.get('run', ''))
    if mutation == 'conditional-live':
        live['if'] = "github.event_name == 'workflow_dispatch'"
    elif mutation == 'ignored-failure':
        live['continue-on-error'] = 'true'
    elif mutation == 'moving-ref':
        package['run'] = package['run'].replace('"$GITHUB_SHA"', 'main')
    else:
        steps.remove(package)
        steps.insert(0, package)
    with pytest.raises(AssertionError):
        assert_workflow_contract(config)


def test_coverage_contract():
    assert_coverage_contract(tomllib.loads((ROOT / 'pyproject.toml').read_text()))


@pytest.mark.parametrize('mutation', ['lower-floor', 'no-branches', 'omit', 'exclude'])
def test_coverage_contract_rejects_weaker_settings(mutation):
    config = tomllib.loads((ROOT / 'pyproject.toml').read_text())
    coverage = config['tool']['coverage']
    if mutation == 'lower-floor':
        coverage['report']['fail_under'] = 99
    elif mutation == 'no-branches':
        coverage['run']['branch'] = False
    elif mutation == 'omit':
        coverage['run']['omit'] = ['tools/verify.py']
    else:
        coverage['report']['exclude_also'] = ['raise ValueError']
    with pytest.raises(AssertionError):
        assert_coverage_contract(config)


def test_owned_tools_have_no_coverage_escape_pragmas():
    forbidden = re.compile(r'pragma:\s*no\s*(?:cover|branch)', re.I)
    for path in (ROOT / 'tools').rglob('*.py'):
        assert not forbidden.search(path.read_text()), path


def test_core_tests_have_no_skip_decorators_or_calls():
    for directory in ('tests', 'tests_live'):
        for path in (ROOT / directory).rglob('test_*.py'):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute):
                    assert node.attr not in {'skip', 'skipif', 'xfail'}, f'{path}:{node.lineno}'


def test_required_main_protection_contract():
    policy = json.loads((ROOT / '.github/main-protection.json').read_text())
    assert policy['required_status_checks'] == {
        'strict': True, 'checks': [{'context': 'verify', 'app_id': 15368}]}
    assert policy['enforce_admins'] is True
    assert policy['required_pull_request_reviews']['required_approving_review_count'] == 0
    assert policy['required_pull_request_reviews']['dismiss_stale_reviews'] is True
    assert policy['required_conversation_resolution'] is True
    assert policy['allow_force_pushes'] is False
    assert policy['allow_deletions'] is False
