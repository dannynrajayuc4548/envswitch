"""Tests for envswitch.cli_lock."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_lock import lock_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles():
    return {"prod": {"KEY": "val"}, "dev": {"KEY": "dev_val"}}


def test_lock_add_success(runner, sample_profiles):
    with patch("envswitch.cli_lock.load_profiles", return_value=sample_profiles), \
         patch("envswitch.cli_lock.is_locked", return_value=False), \
         patch("envswitch.cli_lock.lock_profile") as mock_lock:
        result = runner.invoke(lock_cmd, ["add", "prod"])
        assert result.exit_code == 0
        assert "locked" in result.output
        mock_lock.assert_called_once_with("prod")


def test_lock_add_already_locked(runner, sample_profiles):
    with patch("envswitch.cli_lock.load_profiles", return_value=sample_profiles), \
         patch("envswitch.cli_lock.is_locked", return_value=True):
        result = runner.invoke(lock_cmd, ["add", "prod"])
        assert result.exit_code == 0
        assert "already locked" in result.output


def test_lock_add_profile_not_found(runner):
    with patch("envswitch.cli_lock.load_profiles", return_value={}):
        result = runner.invoke(lock_cmd, ["add", "missing"])
        assert result.exit_code == 1
        assert "not found" in result.output


def test_lock_remove_success(runner):
    with patch("envswitch.cli_lock.is_locked", return_value=True), \
         patch("envswitch.cli_lock.unlock_profile") as mock_unlock:
        result = runner.invoke(lock_cmd, ["remove", "prod"])
        assert result.exit_code == 0
        assert "unlocked" in result.output
        mock_unlock.assert_called_once_with("prod")


def test_lock_remove_not_locked(runner):
    with patch("envswitch.cli_lock.is_locked", return_value=False):
        result = runner.invoke(lock_cmd, ["remove", "prod"])
        assert result.exit_code == 0
        assert "not locked" in result.output


def test_lock_list_empty(runner):
    with patch("envswitch.cli_lock.get_locked_profiles", return_value=[]):
        result = runner.invoke(lock_cmd, ["list"])
        assert result.exit_code == 0
        assert "No locked" in result.output


def test_lock_list_profiles(runner):
    with patch("envswitch.cli_lock.get_locked_profiles", return_value=["prod", "staging"]):
        result = runner.invoke(lock_cmd, ["list"])
        assert result.exit_code == 0
        assert "prod" in result.output
        assert "staging" in result.output


def test_lock_status_locked(runner):
    with patch("envswitch.cli_lock.is_locked", return_value=True):
        result = runner.invoke(lock_cmd, ["status", "prod"])
        assert "is locked" in result.output


def test_lock_status_not_locked(runner):
    with patch("envswitch.cli_lock.is_locked", return_value=False):
        result = runner.invoke(lock_cmd, ["status", "prod"])
        assert "is not locked" in result.output
