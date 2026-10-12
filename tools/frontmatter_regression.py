# Location: tools/frontmatter_regression.py
# Purpose: prove actual launcher rejects malformed skill headers for their cause.
# Functions: mutation_cases, frontmatter_selftest.
# Calls: bounded shell verifier in temporary package copies.
# Imports: json, shutil, subprocess, tempfile, pathlib, release_checks.
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from release_checks import content_hashes
from repo_layout import plugin_root


def mutation_cases(originals):
    good = originals['customer'].splitlines(keepends=True)
    cases = [('quoted colon', 'customer', ''.join(good), True)]
    for name, body in originals.items():
        lines = body.splitlines(keepends=True)
        lines[2] = 'description: ' + json.loads(lines[2].partition(': ')[2]) + '\n'
        cases.append((f'original malformed {name}', name, ''.join(lines), False))
    for label, index, replacement in [
        ('missing opening delimiter', 0, ''), ('missing closing delimiter', 3, ''),
        ('missing description', 2, ''), ('duplicate key', 2, 'name: customer\n'),
        ('empty description', 2, 'description: ""\n'),
        ('non-string description', 2, 'description: 7\n'),
        ('wrong name', 1, 'name: investor\n')]:
        lines = good.copy()
        lines[index] = replacement
        cases.append((label, 'customer', ''.join(lines), False))
    return cases


def frontmatter_selftest(root):
    with tempfile.TemporaryDirectory(prefix='convertia-frontmatter-') as directory:
        fixture = Path(directory) / 'plugin'
        shutil.copytree(plugin_root(root), fixture, ignore=shutil.ignore_patterns(
            '.git', '*.bak', '.venv*', '__pycache__', '.pytest_cache', '.coverage*', 'htmlcov'))
        paths = {name: fixture / f'skills/{name}/SKILL.md' for name in ['customer', 'investor']}
        originals = {name: path.read_text() for name, path in paths.items()}
        for label, name, body, valid in mutation_cases(originals):
            for key, path in paths.items():
                path.write_text(originals[key])
            paths[name].write_text(body)
            (fixture / 'CONTENT.json').write_text(json.dumps(content_hashes(fixture)))
            result = subprocess.run(['bash', str(Path(__file__).with_name('verify.sh')), '--plugin', str(fixture)], cwd=fixture,
                                    text=True, capture_output=True, timeout=30)
            if (result.returncode == 0) != valid or (not valid and 'Invalid skill frontmatter:' not in result.stderr):
                raise RuntimeError(f'Self-test failed: {label}: {result.stdout}{result.stderr}')
            print(f'SELFTEST: {label}: {"accepted" if valid else "rejected for malformed frontmatter"}')
