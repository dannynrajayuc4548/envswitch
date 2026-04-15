"""Tests for the history CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envswitch.cli_history import history_cmd
from envswitch.history import record_switch


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def history_file(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


def test_show_no_history(runner: CliRunner, history_file: Path) -> None:
    with patch("envswitch.cli_history.get_history", return_value=[]):
        result = runner.invoke(history_cmd, ["show"])
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_show_history_entries(runner: CliRunner, history_file: Path) -> None:
    entries = [
        {"profile": "dev", "timestamp": "2024-06-01T10:00:00+00:00"},
        {"profile": "staging", "timestamp": "2024-06-01T11:00:00+00:00"},
    ]
    with patch("envswitch.cli_history.get_history", return_value=entries):
        result = runner.invoke(history_cmd, ["show"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "staging" in result.output


def test_show_history_with_dir(runner: CliRunner) -> None:
    with patch("envswitch.cli_history.get_history", return_value=[]) as mock_get:
        result = runner.invoke(history_cmd, ["show", "--dir", "/some/project"])
    mock_get.assert_called_once_with(cwd="/some/project")
    assert result.exit_code == 0


def test_clear_history_specific_dir(runner: CliRunner) -> None:
    with patch("envswitch.cli_history.clear_history") as mock_clear:
        result = runner.invoke(
            history_cmd, ["clear", "--dir", "/project"], input="y\n"
        )
    mock_clear.assert_called_once_with(cwd="/project")
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_clear_history_all(runner: CliRunner) -> None:
    with patch("envswitch.cli_history.clear_history") as mock_clear:
        result = runner.invoke(history_cmd, ["clear", "--all"], input="y\n")
    mock_clear.assert_called_once_with(cwd=None)
    assert result.exit_code == 0
    assert "All history cleared" in result.output


def test_clear_history_aborted(runner: CliRunner) -> None:
    with patch("envswitch.cli_history.clear_history") as mock_clear:
        result = runner.invoke(history_cmd, ["clear"], input="n\n")
    mock_clear.assert_not_called()
    assert result.exit_code != 0 or "Aborted" in result.output
