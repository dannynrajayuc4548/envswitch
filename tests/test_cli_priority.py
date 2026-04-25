"""CLI tests for envswitch.cli_priority."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envswitch.cli_priority import priority_cmd

SAMPLE_PROFILES = {
    "dev": {"KEY": "val"},
    "prod": {"KEY": "prod-val"},
}


@pytest.fixture()
def runner():
    return CliRunner()


def test_priority_set_success(runner: CliRunner):
    with patch("envswitch.priority.load_profiles", return_value=SAMPLE_PROFILES), \
         patch("envswitch.priority.load_priorities", return_value={}), \
         patch("envswitch.priority.save_priorities") as mock_save:
        result = runner.invoke(priority_cmd, ["set", "dev", "10"])
    assert result.exit_code == 0
    assert "set to 10" in result.output
    mock_save.assert_called_once_with({"dev": 10})


def test_priority_set_profile_not_found(runner: CliRunner):
    with patch("envswitch.priority.load_profiles", return_value=SAMPLE_PROFILES):
        result = runner.invoke(priority_cmd, ["set", "ghost", "5"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_priority_remove_success(runner: CliRunner):
    with patch("envswitch.priority.load_priorities", return_value={"dev": 10}), \
         patch("envswitch.priority.save_priorities") as mock_save:
        result = runner.invoke(priority_cmd, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output
    mock_save.assert_called_once_with({})


def test_priority_remove_not_set(runner: CliRunner):
    with patch("envswitch.priority.load_priorities", return_value={}):
        result = runner.invoke(priority_cmd, ["remove", "dev"])
    assert result.exit_code == 1
    assert "No priority set" in result.output


def test_priority_show_existing(runner: CliRunner):
    with patch("envswitch.priority.load_priorities", return_value={"prod": 99}):
        result = runner.invoke(priority_cmd, ["show", "prod"])
    assert result.exit_code == 0
    assert "prod: 99" in result.output


def test_priority_show_not_set(runner: CliRunner):
    with patch("envswitch.priority.load_priorities", return_value={}):
        result = runner.invoke(priority_cmd, ["show", "dev"])
    assert result.exit_code == 0
    assert "No priority set" in result.output


def test_priority_list_sorted(runner: CliRunner):
    with patch("envswitch.priority.load_priorities",
               return_value={"dev": 5, "prod": 99, "staging": 42}):
        result = runner.invoke(priority_cmd, ["list"])
    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l]
    assert lines[0].startswith("prod")
    assert lines[-1].startswith("dev")


def test_priority_list_empty(runner: CliRunner):
    with patch("envswitch.priority.load_priorities", return_value={}):
        result = runner.invoke(priority_cmd, ["list"])
    assert result.exit_code == 0
    assert "No priorities" in result.output
