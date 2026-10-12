# Location: tests/test_distribution.py
# Purpose: verify subtree distribution commits against temporary Git remotes.
# Functions: publish, provenance, census, freshness and push readback tests.
# Calls: distribution functions, real Git and existing Git test helpers.
# Imports: re, pytest, distribution, test_archive_git, test_repository_policy.
import re

import pytest
import distribution as checks
from test_archive_git import commit_candidate
from test_repository_policy import git


@pytest.fixture
def origin(candidate, tmp_path):
    root = candidate.parents[1]
    remote = tmp_path / 'origin.git'
    git(tmp_path, 'init', '--bare', '-q', str(remote))
    git(root, 'remote', 'add', 'origin', str(remote))
    git(root, 'branch', '-M', 'main')
    git(root, 'push', 'origin', 'main')
    return root


def advance_main(root, candidate):
    readme = root / 'README.md'
    readme.write_text(readme.read_text() + '\nSource-only fixture update.\n')
    commit_candidate(candidate)
    git(root, 'push', 'origin', 'main')
    return git(root, 'rev-parse', 'HEAD')


def test_initial_publication(origin):
    source = git(origin, 'rev-parse', 'HEAD')
    assert checks.remote_refs(origin) == {'refs/heads/main': source}
    published = checks.publish_distribution(origin, source)
    assert re.fullmatch('[0-9a-f]{40}', published)
    assert checks.remote_refs(origin) == {
        'refs/heads/main': source, 'refs/heads/distribution': published}
    assert git(origin, 'rev-parse', published + '^{tree}') == git(
        origin, 'rev-parse', source + ':plugins/convertia')
    assert f'Source-Commit: {source}' in git(
        origin, 'show', '-s', '--format=%B', published).splitlines()
    assert git(origin, 'show', '-s', '--format=%P', published) == ''


def test_publication_is_idempotent(origin):
    source = git(origin, 'rev-parse', 'HEAD')
    first = checks.publish_distribution(origin, source)
    assert checks.publish_distribution(origin, source) == first
    assert checks.remote_refs(origin)['refs/heads/distribution'] == first


def test_new_source_preserves_distribution_history(origin, candidate):
    source = git(origin, 'rev-parse', 'HEAD')
    first = checks.publish_distribution(origin, source)
    updated = advance_main(origin, candidate)
    second = checks.publish_distribution(origin, updated)
    assert second != first
    assert git(origin, 'show', '-s', '--format=%P', second) == first
    assert git(origin, 'rev-parse', second + '^{tree}') == git(
        origin, 'rev-parse', updated + ':plugins/convertia')
    assert f'Source-Commit: {updated}' in git(
        origin, 'show', '-s', '--format=%B', second).splitlines()
    assert checks.remote_refs(origin)['refs/heads/distribution'] == second


def test_stale_source_rejected(origin, candidate):
    source = git(origin, 'rev-parse', 'HEAD')
    updated = advance_main(origin, candidate)
    with pytest.raises(ValueError, match='Stale source'):
        checks.publish_distribution(origin, source)
    assert checks.remote_refs(origin) == {'refs/heads/main': updated}


def test_source_subtree_census(candidate):
    (candidate / 'unexpected.txt').write_text('Unexpected runtime entry.\n')
    commit_candidate(candidate)
    root = candidate.parents[1]
    source = git(root, 'rev-parse', 'HEAD')
    with pytest.raises(ValueError, match='Source subtree census mismatch'):
        checks.runtime_tree(root, source)


def test_validate_distribution_returns_source_tree(origin):
    source = git(origin, 'rev-parse', 'HEAD')
    published = checks.publish_distribution(origin, source)
    assert checks.validate_distribution(origin, source, published) == git(
        origin, 'rev-parse', source + ':plugins/convertia')


def test_distribution_with_repository_tree_rejected(candidate):
    root = candidate.parents[1]
    source = git(root, 'rev-parse', 'HEAD')
    with pytest.raises(ValueError, match='Distribution tree differs'):
        checks.validate_distribution(root, source, source)


def test_distribution_with_wrong_provenance_rejected(candidate):
    root = candidate.parents[1]
    source = git(root, 'rev-parse', 'HEAD')
    tree = git(root, 'rev-parse', source + ':plugins/convertia')
    published = git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                    'commit-tree', tree, '-m', 'Source-Commit: ' + '0' * 40)
    with pytest.raises(ValueError, match='Distribution source provenance mismatch'):
        checks.validate_distribution(root, source, published)


@pytest.mark.parametrize('query,ref,diagnostic', [
    (2, 'refs/heads/main', 'Stale source'),
    (3, 'refs/heads/distribution', 'Distribution push readback mismatch'),
])
def test_remote_change_guards(origin, monkeypatch, query, ref, diagnostic):
    source = git(origin, 'rev-parse', 'HEAD')
    original = checks.remote_refs
    observed = []

    def remote_read(root):
        refs = original(root)
        observed.append(refs.copy())
        if len(observed) == query:
            refs[ref] = '0' * 40
        return refs

    monkeypatch.setattr(checks, 'remote_refs', remote_read)
    with pytest.raises(ValueError, match=diagnostic):
        checks.publish_distribution(origin, source)
    assert len(observed) == query
    actual = original(origin)
    assert actual['refs/heads/main'] == source
    if query == 2:
        assert actual == {'refs/heads/main': source}
    else:
        published = actual['refs/heads/distribution']
        assert observed[-1]['refs/heads/distribution'] == published
        assert checks.validate_distribution(origin, source, published) == git(
            origin, 'rev-parse', source + ':plugins/convertia')
