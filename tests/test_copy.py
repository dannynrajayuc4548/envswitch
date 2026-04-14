"""Tests for profile copy/rename functionality."""

import pytest
from click.testing import CliRunner

from envswitch.cli_copy import copy_cmd, rename_cmd
from envswitch.copy import (
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    copy_profile,
    rename_profile,
)
from envswitch.storage import load_profiles, save_profiles


@pytest.fixture(autouse=True)
def profiles_file(tmp_path, monkeypatch):
    profiles_path = tmp_path / "profiles.json"
    monkeypatch.setattr("envswitch.storage.get_profiles_path", lambda: profiles_path)
    return profiles_path


@pytest.fixture
def sample_profiles():
    data = {
        "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
        "prod": {"DB_HOST": "prod.db", "DEBUG": "false"},
    }
    save_profiles(data)
    return data


def test_copy_profile_success(sample_profiles):
    copy_profile("dev", "staging")
    profiles = load_profiles()
    assert "staging" in profiles
    assert profiles["staging"] == sample_profiles["dev"]
    assert "dev" in profiles  # original still present


def test_copy_profile_not_found():
    with pytest.raises(ProfileNotFoundError):
        copy_profile("nonexistent", "new")


def test_copy_profile_destination_exists_no_overwrite(sample_profiles):
    with pytest.raises(ProfileAlreadyExistsError):
        copy_profile("dev", "prod")


def test_copy_profile_destination_exists_with_overwrite(sample_profiles):
    copy_profile("dev", "prod", overwrite=True)
    profiles = load_profiles()
    assert profiles["prod"] == sample_profiles["dev"]


def test_rename_profile_success(sample_profiles):
    rename_profile("dev", "development")
    profiles = load_profiles()
    assert "development" in profiles
    assert "dev" not in profiles
    assert profiles["development"] == sample_profiles["dev"]


def test_rename_profile_not_found():
    with pytest.raises(ProfileNotFoundError):
        rename_profile("ghost", "spirit")


def test_copy_cmd_success(sample_profiles):
    runner = CliRunner()
    result = runner.invoke(copy_cmd, ["dev", "staging"])
    assert result.exit_code == 0
    assert "copied" in result.output


def test_copy_cmd_not_found():
    runner = CliRunner()
    result = runner.invoke(copy_cmd, ["missing", "new"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_copy_cmd_overwrite(sample_profiles):
    runner = CliRunner()
    result = runner.invoke(copy_cmd, ["dev", "prod", "--overwrite"])
    assert result.exit_code == 0


def test_rename_cmd_success(sample_profiles):
    runner = CliRunner()
    result = runner.invoke(rename_cmd, ["dev", "development"])
    assert result.exit_code == 0
    assert "renamed" in result.output
    profiles = load_profiles()
    assert "development" in profiles
    assert "dev" not in profiles


def test_rename_cmd_conflict_no_overwrite(sample_profiles):
    runner = CliRunner()
    result = runner.invoke(rename_cmd, ["dev", "prod"])
    assert result.exit_code == 1
    assert "already exists" in result.output
