# Location: tests_live/test_github.py
# Purpose: read-only GitHub API and remote artifact connection tests.
# Functions: public_release fixture and live contract assertions.
# Calls: GitHub REST API and codeload HTTPS with default TLS validation.
# Imports: standard library and pytest; no credentials or paid services.
import hashlib
import io
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.github.com/repos/eikiyo/convertia-plugin'


def get(url):
    request = Request(url, headers={'User-Agent': 'Convertia-release-tests'})
    with urlopen(request, timeout=30) as response:
        assert response.status == 200
        return response.read()


@pytest.fixture(scope='module')
def release():
    version = (ROOT / 'VERSION').read_text().strip()
    repository = json.loads(get(API))
    commit = json.loads(get(API + '/commits/' + repository['default_branch']))
    tag = json.loads(get(API + '/commits/v' + version))
    listing = json.loads(get(API + '/releases/tags/v' + version))
    archive = ZipFile(io.BytesIO(get(
        'https://codeload.github.com/eikiyo/convertia-plugin/zip/' + commit['sha'])))
    prefix = archive.namelist()[0]
    files = {name[len(prefix):]: archive.read(name)
             for name in archive.namelist() if not name.endswith('/')}
    return repository, commit, tag, listing, files, version


def test_repository_identity_and_visibility(release):
    repository = release[0]
    assert repository['full_name'] == 'eikiyo/convertia-plugin'
    assert repository['private'] is False
    assert repository['archived'] is False


def test_main_and_immutable_release_tag_agree(release):
    assert release[1]['sha'] == release[2]['sha']


def test_published_release_is_not_draft_or_prerelease(release):
    listing, version = release[3], release[5]
    assert listing['tag_name'] == 'v' + version
    assert listing['draft'] is False
    assert listing['prerelease'] is False


def test_remote_shared_content_equals_candidate(release):
    files = release[4]
    actual = {name: hashlib.sha256(body).hexdigest()
              for name, body in files.items() if name.startswith('skills/')}
    assert actual == json.loads((ROOT / 'CONTENT.json').read_text())


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
