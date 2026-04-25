"""Tests for CLI orchestration."""

from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from commi import cli

runner = CliRunner()


def _always_true(path: Path) -> bool:
    del path
    return True


def _always_false(path: Path) -> bool:
    del path
    return False


def test_run_creates_commit(monkeypatch: MonkeyPatch) -> None:
    """CLI should read staged diff and create commit."""
    commit_message = 'fix: correct typo'
    captured_message = {'value': ''}

    def _fake_read_diff() -> str:
        return 'diff --git a/a.py b/a.py'

    def _fake_generate(diff: str, model_path: str) -> str:
        assert diff
        assert model_path.endswith('commi_model.gguf')
        return commit_message

    def _fake_commit(message: str) -> None:
        captured_message['value'] = message

    monkeypatch.setattr(cli, 'read_staged_diff', _fake_read_diff)
    monkeypatch.setattr(cli, 'generate_commit_message', _fake_generate)
    monkeypatch.setattr(cli, 'create_commit', _fake_commit)
    monkeypatch.setattr(cli, 'MODEL_PATH', Path('/model/commi_model.gguf'))
    monkeypatch.setattr(Path, 'exists', _always_true)

    result = runner.invoke(cli.app, ())

    assert result.exit_code == 0
    assert captured_message['value'] == commit_message
    assert 'The commit was created successfully' in result.stdout


def test_run_fails_when_no_staged_diff(monkeypatch: MonkeyPatch) -> None:
    """CLI should fail if staged diff is empty."""

    def _fake_read_diff() -> str:
        return ''

    monkeypatch.setattr(cli, 'read_staged_diff', _fake_read_diff)

    result = runner.invoke(cli.app, ())

    assert result.exit_code == 1
    assert 'No staged changes found' in result.stdout


def test_run_fails_when_model_not_found(monkeypatch: MonkeyPatch) -> None:
    """CLI should fail when model file is missing."""

    def _fake_read_diff() -> str:
        return 'diff --git a/a.py b/a.py'

    monkeypatch.setattr(cli, 'read_staged_diff', _fake_read_diff)
    monkeypatch.setattr(cli, 'MODEL_PATH', Path('/model/commi_model.gguf'))
    monkeypatch.setattr(Path, 'exists', _always_false)

    result = runner.invoke(cli.app, ())

    assert result.exit_code == 1
    assert 'Model was not found' in result.stdout
