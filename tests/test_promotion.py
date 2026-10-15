# Location: tests/test_promotion.py
# Purpose: enforce exact candidate evidence and CI before release creation.
# Functions: host evidence, CI, GitHub adapter and promotion tests.
# Calls: promotion units, temporary Git commits and independent archive fixtures.
# Imports: datetime, hashlib, json, subprocess, pytest, promotion, conftest, Git helper.
from datetime import datetime, timedelta, timezone
import hashlib
import json
import subprocess

import pytest
import promotion as checks
from conftest import archive_candidate
from test_distribution import origin
from test_repository_policy import git

FIELDS = ('source_commit', 'distribution_commit', 'runtime_tree', 'version', 'archive_sha256')
EXPECTED = dict(zip(FIELDS, ('a' * 40, 'b' * 40, 'c' * 40, '1.5.0', 'd' * 64)))


def make_evidence(expected):
    hosts = {name: {
        **expected, 'status': 'accepted', 'installation_id': 'installed-' + name,
        'evidence_url': 'https://example.invalid/' + name,
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'skills': sorted(checks.SKILLS),
        'smoke': {case: 'passed' for case in checks.SMOKE_CASES},
    } for name in ('claude', 'chatgpt')}
    hosts['chatgpt']['private_overlay_preserved'] = True
    return {**expected, 'hosts': hosts, 'ci_run_id': 123}


@pytest.fixture
def evidence():
    return make_evidence(EXPECTED)


def test_valid_host_evidence(evidence):
    assert checks.check_host_evidence(evidence, *EXPECTED.values()) is None


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
def test_previous_five_case_attestation_cannot_promote_new_features(evidence, host):
    evidence['hosts'][host]['smoke'] = {case: 'passed' for case in (
        'all_skills', 'focused_answer', 'short_followup', 'role_switch', 'due_diligence')}
    with pytest.raises(ValueError, match=f'Host smoke checks incomplete: {host}'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
def test_attestation_predates_candidate(evidence, host):
    minimum = datetime.now(timezone.utc)
    for report in evidence['hosts'].values():
        report['checked_at'] = minimum.isoformat()
    evidence['hosts'][host]['checked_at'] = '2000-01-01T00:00:00+00:00'
    with pytest.raises(ValueError, match=f'Host attestation predates candidate: {host}'):
        checks.check_host_evidence(evidence, *EXPECTED.values(),
                                   not_before=minimum)


@pytest.mark.parametrize('field', FIELDS)
@pytest.mark.parametrize('mutation', ['missing', 'changed'])
def test_top_level_evidence_mismatch(evidence, field, mutation):
    if mutation == 'missing':
        evidence.pop(field)
    else:
        evidence[field] = 'different'
    with pytest.raises(ValueError, match='Stale or mismatched release evidence'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
def test_missing_host(evidence, host):
    evidence['hosts'].pop(host)
    with pytest.raises(ValueError, match='Both host reports'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
def test_malformed_host_report(evidence, host):
    evidence['hosts'][host] = []
    with pytest.raises(ValueError, match='Invalid host report'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
@pytest.mark.parametrize('status', ['pending', 'failed', 'rejected'])
def test_host_not_accepted(evidence, host, status):
    evidence['hosts'][host]['status'] = status
    with pytest.raises(ValueError, match='Host acceptance incomplete'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
@pytest.mark.parametrize('field', FIELDS)
def test_host_candidate_drift(evidence, host, field):
    evidence['hosts'][host][field] = 'different'
    with pytest.raises(ValueError, match='Stale host evidence'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
@pytest.mark.parametrize('installation_id', ['', '  ', None])
def test_missing_installation_identity(evidence, host, installation_id):
    evidence['hosts'][host]['installation_id'] = installation_id
    with pytest.raises(ValueError, match='Missing installed host identity'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
@pytest.mark.parametrize('url', ['', 'http://example.invalid/report', None])
def test_missing_secure_evidence_url(evidence, host, url):
    evidence['hosts'][host]['evidence_url'] = url
    with pytest.raises(ValueError, match='Missing host evidence URL'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
@pytest.mark.parametrize('timestamp', ['', 'invalid-timestamp'])
def test_unparseable_timestamp(evidence, host, timestamp):
    evidence['hosts'][host]['checked_at'] = timestamp
    with pytest.raises(ValueError):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
@pytest.mark.parametrize('kind', ['naive', 'future'])
def test_invalid_timestamp(evidence, host, kind):
    timestamp = datetime.now(timezone.utc)
    timestamp = timestamp.replace(tzinfo=None) if kind == 'naive' else timestamp + timedelta(days=1)
    evidence['hosts'][host]['checked_at'] = timestamp.isoformat()
    with pytest.raises(ValueError, match='Invalid host timestamp'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
def test_missing_skill(evidence, host):
    evidence['hosts'][host]['skills'].pop()
    with pytest.raises(ValueError, match='Host skill census incomplete'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


@pytest.mark.parametrize('host', ['claude', 'chatgpt'])
@pytest.mark.parametrize('case', sorted(checks.SMOKE_CASES))
@pytest.mark.parametrize('mutation', ['pending', 'missing'])
def test_incomplete_smoke(evidence, host, case, mutation):
    smoke = evidence['hosts'][host]['smoke']
    if mutation == 'missing':
        smoke.pop(case)
    else:
        smoke[case] = 'pending'
    with pytest.raises(ValueError, match='Host smoke checks incomplete'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


def test_private_overlay_not_preserved(evidence):
    evidence['hosts']['chatgpt']['private_overlay_preserved'] = False
    with pytest.raises(ValueError, match='Private ChatGPT overlay preservation'):
        checks.check_host_evidence(evidence, *EXPECTED.values())


def ci_response(source):
    return {'head_sha': source, 'head_branch': 'main', 'event': 'push',
            'status': 'completed', 'conclusion': 'success', 'name': 'Verify shared release'}


def capture_github(monkeypatch, run):
    calls = []

    def external(*args):
        calls.append(args)
        return json.dumps(run) if args[0] == 'api' else 'url'

    monkeypatch.setattr(checks, 'github', external)
    return calls


def test_exact_ci_run(monkeypatch):
    source = EXPECTED['source_commit']
    calls = capture_github(monkeypatch, ci_response(source))
    assert checks.check_ci(source, 123) is None
    assert calls == [('api', f'repos/{checks.REPOSITORY}/actions/runs/123')]


@pytest.mark.parametrize('field', ['head_sha', 'head_branch', 'event', 'status', 'conclusion', 'name'])
def test_ci_candidate_mismatch(monkeypatch, field):
    source = EXPECTED['source_commit']
    run = ci_response(source)
    run[field] = 'different'
    calls = capture_github(monkeypatch, run)
    with pytest.raises(ValueError, match='Exact main candidate CI did not pass'):
        checks.check_ci(source, 123)
    assert calls == [('api', f'repos/{checks.REPOSITORY}/actions/runs/123')]


@pytest.mark.parametrize('run_id', [None, 0, True, '123'])
def test_invalid_ci_identity(monkeypatch, run_id):
    calls = capture_github(monkeypatch, ci_response(EXPECTED['source_commit']))
    with pytest.raises(ValueError, match='Missing checked CI run identity'):
        checks.check_ci(EXPECTED['source_commit'], run_id)
    assert calls == []


def test_github_subprocess_adapter(monkeypatch):
    calls = []

    def external_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout='github output\n')

    monkeypatch.setattr(checks.subprocess, 'run', external_run)
    assert checks.github('api', 'repos/example/project') == 'github output\n'
    assert calls == [(['gh', 'api', 'repos/example/project'], {
        'check': True, 'capture_output': True, 'text': True, 'timeout': 60})]


@pytest.fixture
def release_candidate(origin, candidate, tmp_path):
    root = origin
    archive, source = archive_candidate(candidate, tmp_path)
    tree = git(root, 'rev-parse', source + ':plugins/convertia')
    distribution = git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                       'commit-tree', tree, '-m', f'Source-Commit: {source}')
    git(root, 'push', 'origin', f'{distribution}:refs/heads/distribution')
    version = (root / 'plugins/convertia/VERSION').read_text().strip()
    expected = dict(zip(FIELDS, (source, distribution, tree, version,
                                hashlib.sha256(archive.read_bytes()).hexdigest())))
    return root, archive, source, distribution, expected


def advance_remote(root, ref):
    previous = checks.remote_refs(root)['refs/heads/' + ref]
    tree = git(root, 'rev-parse', previous + '^{tree}')
    changed = git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                  'commit-tree', tree, '-p', previous, '-m', 'Remote candidate advanced')
    git(root, 'push', 'origin', f'{changed}:refs/heads/{ref}')


@pytest.mark.parametrize('tag_kind,wrong', [
    ('absent', False), ('lightweight', False), ('annotated', False),
    ('lightweight', True), ('annotated', True),
])
def test_existing_release_tag(release_candidate, tag_kind, wrong):
    root, _, source, distribution, expected = release_candidate
    version = expected['version']
    if tag_kind != 'absent':
        options = ['-am', 'Release attestation'] if tag_kind == 'annotated' else []
        git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
            '-c', 'tag.gpgsign=false', 'tag', *options, f'v{version}',
            distribution if wrong else source)
        git(root, 'push', 'origin', f'refs/tags/v{version}')
    if wrong:
        with pytest.raises(ValueError, match='Existing release tag points to another commit'):
            checks.check_current_candidate(root, source, distribution, version)
    else:
        assert checks.check_current_candidate(root, source, distribution, version) is None


@pytest.mark.parametrize('ref', ['main', 'distribution'])
def test_stale_remote_candidate(release_candidate, ref):
    root, _, source, distribution, expected = release_candidate
    advance_remote(root, ref)
    with pytest.raises(ValueError, match='Stale promotion: remote candidate changed'):
        checks.check_current_candidate(root, source, distribution, expected['version'])


@pytest.mark.parametrize('mode', ['valid', 'bad-host', 'bad-ci', 'stale-main', 'stale-distribution'])
def test_promotion_gate_order(release_candidate, tmp_path, monkeypatch, mode):
    root, archive, source, distribution, expected = release_candidate
    evidence = make_evidence(expected)
    run = ci_response(source)
    if mode == 'bad-host':
        evidence['hosts']['chatgpt']['status'] = 'pending'
    if mode == 'bad-ci':
        run['conclusion'] = 'failure'
    if mode.startswith('stale-'):
        advance_remote(root, mode.removeprefix('stale-'))
    path = tmp_path / 'evidence.json'
    path.write_text(json.dumps(evidence))
    calls = capture_github(monkeypatch, run)
    if mode == 'valid':
        assert checks.promote_release(root, archive, source, distribution, path) == 'url'
    else:
        diagnostic = {'bad-host': 'Host acceptance incomplete', 'bad-ci': 'Exact main candidate CI did not pass',
                      'stale-main': 'Stale promotion', 'stale-distribution': 'Stale promotion'}[mode]
        with pytest.raises(ValueError, match=diagnostic):
            checks.promote_release(root, archive, source, distribution, path)
    api = ('api', f'repos/{checks.REPOSITORY}/actions/runs/123')
    version = expected['version']
    notes = (f'Both-host acceptance attested for version {version}.\nSource: {source}\n'
             f'Distribution: {distribution}\nArchive SHA256: {expected["archive_sha256"]}')
    release = ('release', 'create', f'v{version}', str(archive), '--repo', checks.REPOSITORY,
               '--target', source, '--title', f'Convertia {version}', '--notes', notes)
    assert calls == ([] if mode == 'bad-host' else [api, release] if mode == 'valid' else [api])
