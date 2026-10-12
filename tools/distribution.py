# Location: tools/distribution.py
# Purpose: publish only a verified source subtree to a generated fast-forward branch.
# Functions: runtime_tree, validate_distribution, remote_refs, publish_distribution.
# Calls: Git tree reads, commit-tree and ordinary non-force push.
# Imports: pathlib, archive_checks, release_checks, repo_layout.
from pathlib import Path
from archive_checks import check_commit, git_read, source_files
from release_checks import require
from repo_layout import PLUGIN_PATH


def runtime_tree(root, source):
    check_commit(root, source)
    expected = source_files(root / PLUGIN_PATH, source)
    actual = git_read(root / PLUGIN_PATH, 'ls-tree', '-r', '--name-only', '-z', source).decode().split('\0')
    require(set(actual) - {''} == set(expected), 'Source subtree census mismatch')
    return git_read(root, 'rev-parse', f'{source}:{PLUGIN_PATH}').decode().strip()


def validate_distribution(root, source, distribution):
    root = Path(root)
    tree = runtime_tree(root, source)
    check_commit(root, distribution)
    require(git_read(root, 'rev-parse', f'{distribution}^{{tree}}').decode().strip() == tree,
            'Distribution tree differs from checked source')
    message = git_read(root, 'show', '-s', '--format=%B', distribution).decode().splitlines()
    require(f'Source-Commit: {source}' in message, 'Distribution source provenance mismatch')
    return tree


def remote_refs(root):
    lines = git_read(root, 'ls-remote', '--heads', 'origin',
                     'refs/heads/main', 'refs/heads/distribution').decode().splitlines()
    return {line.split()[1]: line.split()[0] for line in lines}


def publish_distribution(root, source):
    root = Path(root)
    tree = runtime_tree(root, source)
    refs = remote_refs(root)
    require(refs.get('refs/heads/main') == source, 'Stale source: remote main changed')
    previous = refs.get('refs/heads/distribution')
    parents = []
    if previous:
        git_read(root, 'fetch', '--no-tags', 'origin', previous)
        old_message = git_read(root, 'show', '-s', '--format=%B', previous).decode().splitlines()
        if f'Source-Commit: {source}' in old_message:
            validate_distribution(root, source, previous)
            return previous
        parents = ['-p', previous]
    commit = git_read(root, '-c', 'user.name=Convertia release', '-c',
                      'user.email=release@users.noreply.github.com', 'commit-tree', tree,
                      *parents, '-m', f'Generated Convertia candidate\n\nSource-Commit: {source}').decode().strip()
    validate_distribution(root, source, commit)
    require(remote_refs(root).get('refs/heads/main') == source, 'Stale source: remote main changed')
    git_read(root, 'push', 'origin', f'{commit}:refs/heads/distribution')
    require(remote_refs(root).get('refs/heads/distribution') == commit, 'Distribution push readback mismatch')
    return commit
