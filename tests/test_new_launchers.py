# Location: tests/test_new_launchers.py
# Purpose: execute release wrappers against real local repositories and artifacts.
# Functions: external command fixtures and wrapper success/failure controls.
# Calls: shell wrappers, Git, real validators and temporary npm/gh executables.
# Imports: hashlib, json, os, sys, zipfile, pytest, conftest and shared test helpers.
import hashlib
import json
import os
import sys
import zipfile

import pytest
from conftest import ROOT, archive_candidate
from distribution import remote_refs
from test_distribution import origin, advance_main
from test_e2e import launcher_env, run_command
from test_promotion import make_evidence, ci_response
from test_repository_policy import git


def external_command(tmp_path, name, body):
    directory = tmp_path / 'commands'
    directory.mkdir(exist_ok=True)
    command = directory / name
    command.write_text('#!/bin/bash\nset -euo pipefail\n' + body)
    command.chmod(0o755)
    log = tmp_path / (name + '.calls')
    log.write_bytes(b'')
    env = launcher_env()
    env['PATH'] = str(directory) + os.pathsep + env['PATH']
    env['BOUNDARY_LOG'] = str(log)
    return env, log


def isolated_python(repository):
    (repository / '.venv').symlink_to(ROOT / '.venv', target_is_directory=True)
    with (repository / '.git/info/exclude').open('a') as exclude:
        exclude.write('\n/.venv\n')


@pytest.mark.parametrize('invalid', [False, True])
def test_repository_wrapper(candidate, tmp_path, invalid):
    repository = candidate.parents[1]
    isolated_python(repository)
    if invalid:
        (candidate / 'unknown.txt').write_text('Unexpected runtime content')
    result = run_command(['bash', str(repository / 'tools/verify-repository.sh')],
                         tmp_path, launcher_env())
    if invalid:
        assert result.returncode != 0
        assert 'Plugin census' in result.stderr
    else:
        assert result.returncode == 0, result.stderr
        assert 'repository policy passed' in result.stdout


@pytest.mark.parametrize('invalid', [False, True])
def test_official_wrapper(candidate, tmp_path, invalid):
    repository = candidate.parents[1]
    archive, _ = archive_candidate(candidate, tmp_path)
    shipped = tmp_path / 'shipped'
    with zipfile.ZipFile(archive) as package:
        package.extractall(shipped)
    isolated_python(repository)
    env, log = external_command(tmp_path, 'npm',
        'if [[ ${ANTHROPIC_TEST_SECRET+x} == x ]]; then exit 91; fi\n'
        'printf "%s\\n" "$*" >> "$BOUNDARY_LOG"\n')
    env['ANTHROPIC_TEST_SECRET'] = 'synthetic-fixture'
    if invalid:
        manifest = shipped / 'plugin.json'
        data = json.loads(manifest.read_text())
        data['name'] = 42
        manifest.write_text(json.dumps(data))
    result = run_command(['bash', str(repository / 'tools/verify-official.sh'), str(shipped)],
                         tmp_path, env)
    if invalid:
        assert result.returncode != 0
        assert 'ValidationError' in result.stderr
        assert log.read_text() == ''
    else:
        assert result.returncode == 0, result.stderr
        assert 'PASS: official portable schema and all 11 Agent Skills entrypoints' in result.stdout
        targets = ['.claude-plugin/marketplace.json',
                   'plugins/convertia/.claude-plugin/plugin.json',
                   str(shipped / '.claude-plugin/marketplace.json'),
                   str(shipped / '.claude-plugin/plugin.json')]
        assert log.read_text().splitlines() == [
            'exec --yes --package=@anthropic-ai/claude-code@2.1.296 -- '
            f'claude plugin validate {target} --strict' for target in targets]


@pytest.mark.parametrize('stale', [False, True])
def test_publish_wrapper(origin, candidate, tmp_path, stale):
    source = git(origin, 'rev-parse', 'HEAD')
    if stale:
        advance_main(origin, candidate)
    before = remote_refs(origin)
    result = run_command(['bash', str(origin / 'tools/publish-distribution.sh'), source],
                         tmp_path, launcher_env())
    if stale:
        assert result.returncode != 0
        assert 'Stale source' in result.stderr
        assert remote_refs(origin) == before
    else:
        assert result.returncode == 0, result.stderr
        published = result.stdout.strip()
        assert remote_refs(origin) == {
            'refs/heads/main': source, 'refs/heads/distribution': published}
        assert git(origin, 'rev-parse', published + '^{tree}') == git(
            origin, 'rev-parse', source + ':plugins/convertia')


def test_publisher_import_uses_only_standard_library(repository, tmp_path):
    code = ('import sys; sys.path.insert(0, sys.argv[1]); '
            'import distribution; print("distribution imported without site packages")')
    result = run_command([sys.executable, '-I', '-S', '-c', code,
                          str(repository / 'tools')], tmp_path, launcher_env())
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'distribution imported without site packages'


@pytest.fixture
def promotion_input(origin, candidate, tmp_path):
    archive, source = archive_candidate(candidate, tmp_path)
    tree = git(origin, 'rev-parse', source + ':plugins/convertia')
    distribution = git(origin, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                       'commit-tree', tree, '-m', f'Source-Commit: {source}')
    git(origin, 'push', 'origin', distribution + ':refs/heads/distribution')
    version = (candidate / 'VERSION').read_text().strip()
    expected = {'source_commit': source, 'distribution_commit': distribution,
                'runtime_tree': tree, 'version': version,
                'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
    isolated_python(origin)
    return origin, archive, expected


@pytest.mark.parametrize('pending', [False, True])
def test_promotion_wrapper(promotion_input, tmp_path, pending):
    repository, archive, expected = promotion_input
    evidence = make_evidence(expected)
    if pending:
        evidence['hosts']['chatgpt']['status'] = 'pending'
    evidence_path = tmp_path / 'evidence.json'
    evidence_path.write_text(json.dumps(evidence))
    response = tmp_path / 'ci.json'
    response.write_text(json.dumps(ci_response(expected['source_commit'])))
    env, log = external_command(tmp_path, 'gh',
        'if [[ "$1" == "api" ]]; then\n  cat "$CI_RESPONSE"\n'
        'else\n  printf "%s\\0" "$@" >> "$BOUNDARY_LOG"\n'
        '  printf "%s\\n" "https://example.invalid/release"\nfi\n')
    env['CI_RESPONSE'] = str(response)
    result = run_command(['bash', str(repository / 'tools/promote-release.sh'), str(archive),
                          expected['source_commit'], expected['distribution_commit'],
                          str(evidence_path)], tmp_path, env)
    if pending:
        assert result.returncode != 0
        assert 'Host acceptance incomplete: chatgpt' in result.stderr
        assert log.read_bytes() == b''
    else:
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == 'https://example.invalid/release'
        arguments = log.read_bytes().decode().split('\0')[:-1]
        assert arguments[:4] == ['release', 'create', 'v' + expected['version'], str(archive)]
        assert arguments[4:10] == ['--repo', 'eikiyo/convertia-plugin', '--target',
                                   expected['source_commit'], '--title',
                                   'Convertia ' + expected['version']]
        assert arguments[10] == '--notes'
        assert 'Archive SHA256: ' + expected['archive_sha256'] in arguments[11]
