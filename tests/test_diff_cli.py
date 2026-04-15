import json
import pytest
from click.testing import CliRunner
from envswitch.diff_cli import diff_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles(tmp_path, monkeypatch):
    profiles = {
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"},
        "prod": {"DB_HOST": "db.example.com", "DB_PORT": "5432", "LOG_LEVEL": "warn"},
    }
    profiles_file = tmp_path / "profiles.json"
    profiles_file.write_text(json.dumps(profiles))
    monkeypatch.setattr("envswitch.storage.get_profiles_path", lambda: profiles_file)
    return profiles


def test_diff_shows_added_vars(runner, sample_profiles):
    result = runner.invoke(diff_cmd, ["dev", "prod", "--no-color"])
    assert result.exit_code == 0
    assert "+" in result.output
    assert "LOG_LEVEL" in result.output


def test_diff_shows_removed_vars(runner, sample_profiles):
    result = runner.invoke(diff_cmd, ["dev", "prod", "--no-color"])
    assert result.exit_code == 0
    assert "-" in result.output
    assert "DEBUG" in result.output


def test_diff_shows_changed_vars(runner, sample_profiles):
    result = runner.invoke(diff_cmd, ["dev", "prod", "--no-color"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_diff_identical_profiles(runner, tmp_path, monkeypatch):
    profiles = {"a": {"KEY": "val"}, "b": {"KEY": "val"}}
    profiles_file = tmp_path / "profiles.json"
    profiles_file.write_text(json.dumps(profiles))
    monkeypatch.setattr("envswitch.storage.get_profiles_path", lambda: profiles_file)

    result = runner.invoke(diff_cmd, ["a", "b"])
    assert result.exit_code == 0
    assert "identical" in result.output


def test_diff_profile_not_found(runner, sample_profiles):
    result = runner.invoke(diff_cmd, ["dev", "nonexistent"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_diff_both_profiles_not_found(runner, sample_profiles):
    result = runner.invoke(diff_cmd, ["ghost", "phantom"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_diff_no_color_flag(runner, sample_profiles):
    result = runner.invoke(diff_cmd, ["dev", "prod", "--no-color"])
    assert result.exit_code == 0
    # Output should not contain ANSI escape codes
    assert "\x1b[" not in result.output
