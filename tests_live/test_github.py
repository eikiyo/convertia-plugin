# Location: tests_live/test_github.py
# Purpose: read-only GitHub API and remote artifact connection tests.
# Functions: public_release fixture and live contract assertions.
# Calls: GitHub REST API and codeload HTTPS with default TLS validation.
# Imports: standard library and pytest; no credentials or paid services.
import hashlib
import io
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pytest

API = 'https://api.github.com/repos/eikiyo/convertia-plugin'


def get(url):
    request = Request(url, headers={'User-Agent': 'Convertia-release-tests'})
    with urlopen(request, timeout=30) as response:
        assert response.status == 200
        return response.read()


@pytest.fixture(scope='module')
def release():
    repository = json.loads(get(API))
    listing = json.loads(get(API + '/releases/latest'))
    tag_name = listing['tag_name']
    commit = json.loads(get(API + '/commits/' + tag_name))
    archive = ZipFile(io.BytesIO(get(
        'https://codeload.github.com/eikiyo/convertia-plugin/zip/' + commit['sha'])))
    prefix = archive.namelist()[0]
    files = {name[len(prefix):]: archive.read(name)
             for name in archive.namelist() if not name.endswith('/')}
    if 'plugins/convertia/plugin.json' in files:
        files = {name.removeprefix('plugins/convertia/'): body for name, body in files.items()
                 if name.startswith('plugins/convertia/')}
    return repository, commit, prefix, listing, files, tag_name.removeprefix('v')


def test_repository_identity_and_visibility(release):
    repository = release[0]
    assert repository['full_name'] == 'eikiyo/convertia-plugin'
    assert repository['private'] is False
    assert repository['archived'] is False


def test_published_tag_resolves_to_archived_commit(release):
    commit, prefix = release[1:3]
    assert len(commit['sha']) == 40
    assert prefix == 'convertia-plugin-' + commit['sha'] + '/'


def test_published_release_is_not_draft_or_prerelease(release):
    listing, version = release[3], release[5]
    assert listing['tag_name'] == 'v' + version
    assert listing['draft'] is False
    assert listing['prerelease'] is False


def test_published_archive_matches_its_own_content_lock(release):
    files = release[4]
    actual = {name: hashlib.sha256(body).hexdigest()
              for name, body in files.items() if name.startswith('skills/')}
    assert actual == json.loads(files['CONTENT.json'])


def test_remote_manifests_agree(release):
    files, version = release[4:]
    for name in ('plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json'):
        data = json.loads(files[name])
        assert data['name'] == 'convertia'
        assert data['version'] == version
    assert files['VERSION'].decode().strip() == version


def test_remote_archive_has_no_backup_or_mcp(release):
    names = release[4]
    assert '.mcp.json' not in names
    assert not any(name.endswith(('.bak', '.pdf')) for name in names)


def test_missing_ref_returns_explicit_validation_error():
    with pytest.raises(HTTPError) as error:
        get(API + '/commits/convertia-test-deliberately-missing-ref')
    assert error.value.code == 422
    payload = json.loads(error.value.read())
    assert 'No commit found for SHA' in payload['message']
