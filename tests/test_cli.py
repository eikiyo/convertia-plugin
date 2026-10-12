# Location: tests/test_cli.py
# Purpose: exercise CLI success and failure paths and regression-test controls.
# Functions: main entrypoint and selftest boundary tests.
# Calls: real main and selftest; subprocess responses injected only for negative controls.
# Imports: subprocess, sys, pytest, verify, frontmatter_regression.
import subprocess
import sys
import pytest
from conftest import expected_pass
import verify
import frontmatter_regression as regression


def test_main_default(package, monkeypatch, capsys):
    monkeypatch.chdir(package)
    monkeypatch.setattr(sys, 'argv', ['verify'])
    monkeypatch.delenv('PREVIOUS_VERSION', raising=False)
    assert verify.main() == 0
    assert capsys.readouterr().out.strip() == expected_pass(package)


def test_main_bad_argument(package, capsys):
    assert verify.main(['--unknown'], package) == 1
    assert 'Usage:' in capsys.readouterr().err


def test_main_external_plugin(package, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('PREVIOUS_VERSION', raising=False)
    assert verify.main(['--plugin', str(package)]) == 0
    assert capsys.readouterr().out.strip() == expected_pass(package)
    (package / 'VERSION').write_text('invalid')
    assert verify.main(['--plugin', str(package)]) == 1
    assert 'Invalid VERSION' in capsys.readouterr().err


def test_main_read_error(package, capsys):
    (package / 'VERSION').unlink()
    assert verify.main([], package) == 1
    assert 'FAIL:' in capsys.readouterr().err


def test_main_previous_version(package, monkeypatch, capsys):
    monkeypatch.setenv('PREVIOUS_VERSION', '99.0.0')
    assert verify.main([], package) == 1
    assert 'Version must increase' in capsys.readouterr().err


def test_main_selftest(package, monkeypatch, capsys):
    monkeypatch.delenv('PREVIOUS_VERSION', raising=False)
    assert verify.main(['--self-test'], package) == 0
    output = capsys.readouterr().out
    assert output.count('SELFTEST:') == 10
    assert 'original malformed customer: rejected for malformed frontmatter' in output
    assert 'original malformed investor: rejected for malformed frontmatter' in output


@pytest.mark.parametrize('responses', [
    [(1, 'other failure')],
    [(0, ''), (0, '')],
    [(0, ''), (1, 'Content lock drift')],
])
def test_selftest_rejects_false_results(package, monkeypatch, responses):
    results = iter(responses)
    def fake_process(*args, **kwargs):
        status, error = next(results)
        return subprocess.CompletedProcess(args[0], status, '', error)
    monkeypatch.setattr(regression.subprocess, 'run', fake_process)
    with pytest.raises(RuntimeError, match='Self-test failed:'):
        regression.frontmatter_selftest(package)


def test_selftest_propagates_execution_failure(package, monkeypatch, capsys):
    def fail_process(*args, **kwargs):
        raise OSError('launcher unavailable')
    monkeypatch.setattr(regression.subprocess, 'run', fail_process)
    assert verify.main(['--self-test'], package) == 1
    assert 'FAIL: launcher unavailable' in capsys.readouterr().err


def test_selftest_timeout(package, monkeypatch, capsys):
    def timeout_process(*args, **kwargs):
        raise subprocess.TimeoutExpired('verifier', 30)
    monkeypatch.setattr(regression.subprocess, 'run', timeout_process)
    assert verify.main(['--self-test'], package) == 1
    assert 'timed out' in capsys.readouterr().err
