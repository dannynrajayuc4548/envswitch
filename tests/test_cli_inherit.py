"""Tests for the inherit CLI commands."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_inherit import inherit_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles():
    return {
        "base": {"DB_HOST": "localhost", "DB_PORT": "5432"},
        "dev": {"__base__": "base", "DEBUG": "true"},
        "prod": {"DB_HOST": "prod.db", "DB_PORT": "5432", "DEBUG": "false"},
    }


def test_inherit_set_success(runner, sample_profiles):
    with patch("envswitch.cli_inherit.load_profiles", return_value=sample_profiles), \
         patch("envswitch.cli_inherit.set_base") as mock_set:
        result = runner.invoke(inherit_cmd, ["set", "dev", "base"])
        assert result.exit_code == 0
        assert "base" in result.output
        mock_set.assert_called_once_with("dev", "base")


def test_inherit_set_profile_not_found(runner, sample_profiles):
    from envswitch.inherit import ProfileNotFoundError
    with patch("envswitch.cli_inherit.load_profiles", return_value=sample_profiles), \
         patch("envswitch.cli_inherit.set_base", side_effect=ProfileNotFoundError("ghost")):
        result = runner.invoke(inherit_cmd, ["set", "ghost", "base"])
        assert result.exit_code != 0 or "not found" in result.output.lower()


def test_inherit_set_circular(runner, sample_profiles):
    from envswitch.inherit import CircularInheritanceError
    with patch("envswitch.cli_inherit.load_profiles", return_value=sample_profiles), \
         patch("envswitch.cli_inherit.set_base", side_effect=CircularInheritanceError("cycle")):
        result = runner.invoke(inherit_cmd, ["set", "base", "dev"])
        assert "circular" in result.output.lower() or result.exit_code != 0


def test_inherit_remove_success(runner, sample_profiles):
    with patch("envswitch.cli_inherit.load_profiles", return_value=sample_profiles), \
         patch("envswitch.cli_inherit.remove_base") as mock_remove:
        result = runner.invoke(inherit_cmd, ["remove", "dev"])
        assert result.exit_code == 0
        mock_remove.assert_called_once_with("dev")


def test_inherit_remove_not_found(runner, sample_profiles):
    from envswitch.inherit import ProfileNotFoundError
    with patch("envswitch.cli_inherit.load_profiles", return_value=sample_profiles), \
         patch("envswitch.cli_inherit.remove_base", side_effect=ProfileNotFoundError("ghost")):
        result = runner.invoke(inherit_cmd, ["remove", "ghost"])
        assert "not found" in result.output.lower() or result.exit_code != 0


def test_inherit_show_with_base(runner, sample_profiles):
    resolved = {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"}
    with patch("envswitch.cli_inherit.load_profiles", return_value=sample_profiles), \
         patch("envswitch.cli_inherit.resolve_profile", return_value=resolved):
        result = runner.invoke(inherit_cmd, ["show", "dev"])
        assert result.exit_code == 0
        assert "DB_HOST" in result.output
        assert "DEBUG" in result.output


def test_inherit_show_profile_not_found(runner, sample_profiles):
    from envswitch.inherit import ProfileNotFoundError
    with patch("envswitch.cli_inherit.load_profiles", return_value=sample_profiles), \
         patch("envswitch.cli_inherit.resolve_profile", side_effect=ProfileNotFoundError("ghost")):
        result = runner.invoke(inherit_cmd, ["show", "ghost"])
        assert "not found" in result.output.lower() or result.exit_code != 0


def test_inherit_list_shows_profiles_with_bases(runner, sample_profiles):
    with patch("envswitch.cli_inherit.load_profiles", return_value=sample_profiles):
        result = runner.invoke(inherit_cmd, ["list"])
        assert result.exit_code == 0
        assert "dev" in result.output
        assert "base" in result.output


def test_inherit_list_no_profiles(runner):
    with patch("envswitch.cli_inherit.load_profiles", return_value={}):
        result = runner.invoke(inherit_cmd, ["list"])
        assert result.exit_code == 0
