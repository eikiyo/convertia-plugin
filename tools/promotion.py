# Location: tools/promotion.py
# Purpose: create a release only after checked CI and exact two-host acceptance evidence.
# Functions: host evidence validation, GitHub read checks and gated promotion.
# Calls: shared archive/provenance checks and gh release create after every gate.
# Imports: datetime, hashlib, json, subprocess, pathlib, archive_checks, distribution, release_checks.
from datetime import datetime, timezone
import hashlib
import json
import subprocess
from pathlib import Path
from archive_checks import git_read, validate_archive
from distribution import validate_distribution, remote_refs
from release_checks import read_json, require, SKILLS

REPOSITORY = 'eikiyo/convertia-plugin'
SMOKE_CASES = {'all_skills', 'focused_answer', 'short_followup', 'role_switch', 'due_diligence',
               'natural_language_artifact', 'artifact_create_open', 'artifact_revision_export',
               'artifact_unavailable', 'legal_bilingual', 'regulation_bilingual',
               'bilingual_revision', 'language_and_terms', 'artifact_focus_return',
               'no_artifact_on_followup'}


def check_host_evidence(evidence, source, distribution, tree, version, digest,
                        not_before=datetime(1970, 1, 1, tzinfo=timezone.utc)):
    expected = {'source_commit': source, 'distribution_commit': distribution,
                'runtime_tree': tree, 'version': version, 'archive_sha256': digest}
    require(all(evidence.get(key) == value for key, value in expected.items()), 'Stale or mismatched release evidence')
    hosts = evidence.get('hosts')
    require(isinstance(hosts, dict) and set(hosts) == {'claude', 'chatgpt'}, 'Both host reports are required')
    for name, report in hosts.items():
        require(isinstance(report, dict), f'Invalid host report: {name}')
        require(report.get('status') == 'accepted', f'Host acceptance incomplete: {name}')
        require(all(report.get(key) == value for key, value in expected.items()), f'Stale host evidence: {name}')
        require(isinstance(report.get('installation_id'), str) and report['installation_id'].strip(),
                f'Missing installed host identity: {name}')
        require(isinstance(report.get('evidence_url'), str) and report['evidence_url'].startswith('https://'),
                f'Missing host evidence URL: {name}')
        checked = datetime.fromisoformat(report.get('checked_at', ''))
        require(checked.tzinfo is not None and checked <= datetime.now(timezone.utc), f'Invalid host timestamp: {name}')
        require(checked >= not_before, f'Host attestation predates candidate: {name}')
        require(report.get('skills') == sorted(SKILLS), f'Host skill census incomplete: {name}')
        require(report.get('smoke') == {case: 'passed' for case in SMOKE_CASES}, f'Host smoke checks incomplete: {name}')
    require(hosts['chatgpt'].get('private_overlay_preserved') is True, 'Private ChatGPT overlay preservation unverified')


def github(*args):
    return subprocess.run(['gh', *args], check=True, capture_output=True, text=True, timeout=60).stdout


def check_ci(source, run_id):
    require(isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0, 'Missing checked CI run identity')
    run = json.loads(github('api', f'repos/{REPOSITORY}/actions/runs/{run_id}'))
    require(all(run.get(key) == value for key, value in {
        'head_sha': source, 'head_branch': 'main', 'event': 'push',
        'status': 'completed', 'conclusion': 'success', 'name': 'Verify shared release'}.items()),
        'Exact main candidate CI did not pass')


def check_current_candidate(root, source, distribution, version):
    refs = remote_refs(root)
    require(refs.get('refs/heads/main') == source and refs.get('refs/heads/distribution') == distribution,
            'Stale promotion: remote candidate changed')
    tag = 'refs/tags/v' + version
    rows = git_read(root, 'ls-remote', '--tags', 'origin', tag, tag + '^{}').decode().splitlines()
    tags = {line.split()[1]: line.split()[0] for line in rows}
    target = tags.get(tag + '^{}', tags.get(tag))
    require(target is None or target == source, 'Existing release tag points to another commit')


def promote_release(root, archive_path, source, distribution, evidence_path):
    root, archive_path = Path(root), Path(archive_path)
    tree = validate_distribution(root, source, distribution)
    validate_archive(archive_path, root, source)
    version = git_read(root, 'show', f'{source}:plugins/convertia/VERSION').decode().strip()
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    evidence = read_json(Path(evidence_path))
    created = datetime.fromtimestamp(int(git_read(root, 'show', '-s', '--format=%ct', source)), timezone.utc)
    check_host_evidence(evidence, source, distribution, tree, version, digest, created)
    check_ci(source, evidence.get('ci_run_id'))
    check_current_candidate(root, source, distribution, version)
    notes = f'Both-host acceptance attested for version {version}.\nSource: {source}\nDistribution: {distribution}\nArchive SHA256: {digest}'
    return github('release', 'create', 'v' + version, str(archive_path), '--repo', REPOSITORY,
                  '--target', source, '--title', 'Convertia ' + version, '--notes', notes)
