"""Tests for the CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envswitch.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles():
    return {
        "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
        "prod": {"DB_HOST": "db.prod.example.com", "DEBUG": "false"},
    }


def test_list_no_profiles(runner):
    with patch("envswitch.cli.list_profiles", return_value=[]):
        result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No profiles found" in result.output


def test_list_profiles(runner, sample_profiles):
    with patch("envswitch.cli.list_profiles", return_value=list(sample_profiles.keys())):
        result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_show_existing_profile(runner, sample_profiles):
    with patch("envswitch.cli.get_profile", return_value=sample_profiles["dev"]):
        result = runner.invoke(cli, ["show", "dev"])
    assert result.exit_code == 0
    assert "DB_HOST=localhost" in result.output
    assert "DEBUG=true" in result.output


def test_show_missing_profile(runner):
    with patch("envswitch.cli.get_profile", return_value=None):
        result = runner.invoke(cli, ["show", "nonexistent"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_set_variable(runner):
    profiles = {"dev": {}}
    with patch("envswitch.cli.load_profiles", return_value=profiles), \
         patch("envswitch.cli.save_profiles") as mock_save:
        result = runner.invoke(cli, ["set", "dev", "MY_VAR", "hello"])
    assert result.exit_code == 0
    assert "Set MY_VAR=hello" in result.output
    mock_save.assert_called_once()


def test_set_variable_creates_new_profile(runner):
    with patch("envswitch.cli.load_profiles", return_value={}), \
         patch("envswitch.cli.save_profiles") as mock_save:
        result = runner.invoke(cli, ["set", "newprofile", "FOO", "bar"])
    assert result.exit_code == 0
    saved_profiles = mock_save.call_args[0][0]
    assert "newprofile" in saved_profiles
    assert saved_profiles["newprofile"]["FOO"] == "bar"


def test_delete_profile_with_yes_flag(runner):
    with patch("envswitch.cli.delete_profile", return_value=True) as mock_delete:
        result = runner.invoke(cli, ["delete", "dev", "--yes"])
    assert result.exit_code == 0
    assert "deleted" in result.output
    mock_delete.assert_called_once_with("dev")


def test_delete_missing_profile(runner):
    with patch("envswitch.cli.delete_profile", return_value=False):
        result = runner.invoke(cli, ["delete", "ghost", "--yes"])
    assert result.exit_code == 1


def test_export_bash(runner, sample_profiles):
    with patch("envswitch.cli.get_profile", return_value=sample_profiles["dev"]):
        result = runner.invoke(cli, ["export", "dev", "--shell", "bash"])
    assert result.exit_code == 0
    assert "export DB_HOST=localhost" in result.output


def test_export_fish(runner, sample_profiles):
    with patch("envswitch.cli.get_profile", return_value=sample_profiles["dev"]):
        result = runner.invoke(cli, ["export", "dev", "--shell", "fish"])
    assert result.exit_code == 0
    assert "set -x DB_HOST localhost" in result.output
