"""Tests for envswitch.merge module."""

import json
import pytest
from pathlib import Path
from envswitch.merge import merge_profiles, ProfileNotFoundError, ProfileAlreadyExistsError


@pytest.fixture
def profiles_file(tmp_path: Path) -> Path:
    path = tmp_path / "profiles.json"
    data = {
        "base": {"APP_ENV": "production", "LOG_LEVEL": "info"},
        "staging": {"APP_ENV": "staging", "DEBUG": "true"},
        "extras": {"EXTRA_VAR": "hello"},
    }
    path.write_text(json.dumps(data))
    return path


def test_merge_two_profiles(profiles_file: Path) -> None:
    merged = merge_profiles(["base", "staging"], "merged", profiles_path=str(profiles_file))
    assert merged["APP_ENV"] == "staging"  # staging overrides base
    assert merged["LOG_LEVEL"] == "info"   # from base
    assert merged["DEBUG"] == "true"        # from staging


def test_merge_three_profiles(profiles_file: Path) -> None:
    merged = merge_profiles(["base", "staging", "extras"], "full", profiles_path=str(profiles_file))
    assert merged["EXTRA_VAR"] == "hello"
    assert merged["APP_ENV"] == "staging"


def test_merge_saves_to_profiles(profiles_file: Path) -> None:
    merge_profiles(["base", "staging"], "merged", profiles_path=str(profiles_file))
    data = json.loads(profiles_file.read_text())
    assert "merged" in data


def test_merge_source_not_found(profiles_file: Path) -> None:
    with pytest.raises(ProfileNotFoundError, match="nonexistent"):
        merge_profiles(["base", "nonexistent"], "out", profiles_path=str(profiles_file))


def test_merge_destination_exists_no_overwrite(profiles_file: Path) -> None:
    with pytest.raises(ProfileAlreadyExistsError, match="base"):
        merge_profiles(["staging", "extras"], "base", profiles_path=str(profiles_file))


def test_merge_destination_exists_with_overwrite(profiles_file: Path) -> None:
    merged = merge_profiles(
        ["staging", "extras"], "base", overwrite=True, profiles_path=str(profiles_file)
    )
    assert merged["EXTRA_VAR"] == "hello"


def test_merge_requires_at_least_two_sources(profiles_file: Path) -> None:
    # merge_profiles itself does not enforce this; CLI does. Single source still works.
    merged = merge_profiles(["base"], "single_out", profiles_path=str(profiles_file))
    assert merged == {"APP_ENV": "production", "LOG_LEVEL": "info"}
