"""Tests for the envswitch storage module."""

import json
import pytest
from pathlib import Path

from envswitch.storage import (
    load_profiles,
    save_profiles,
    get_profile,
    set_profile,
    delete_profile,
    list_profile_names,
)


@pytest.fixture
def profiles_file(tmp_path):
    """Return a temporary path for a profiles JSON file."""
    return tmp_path / "profiles.json"


def test_load_profiles_missing_file(profiles_file):
    assert load_profiles(profiles_file) == {}


def test_save_and_load_profiles(profiles_file):
    data = {"dev": {"DEBUG": "1", "DB_URL": "sqlite:///dev.db"}}
    save_profiles(data, profiles_file)
    assert profiles_file.exists()
    loaded = load_profiles(profiles_file)
    assert loaded == data


def test_load_profiles_invalid_format(profiles_file):
    profiles_file.write_text("[1, 2, 3]")
    with pytest.raises(ValueError, match="Invalid profiles file format"):
        load_profiles(profiles_file)


def test_get_profile_existing(profiles_file):
    set_profile("staging", {"ENV": "staging"}, profiles_file)
    result = get_profile("staging", profiles_file)
    assert result == {"ENV": "staging"}


def test_get_profile_missing(profiles_file):
    assert get_profile("nonexistent", profiles_file) is None


def test_set_profile_creates_new(profiles_file):
    set_profile("prod", {"ENV": "production", "PORT": "8080"}, profiles_file)
    profiles = load_profiles(profiles_file)
    assert "prod" in profiles
    assert profiles["prod"]["PORT"] == "8080"


def test_set_profile_overwrites_existing(profiles_file):
    set_profile("dev", {"DEBUG": "1"}, profiles_file)
    set_profile("dev", {"DEBUG": "0", "NEW_VAR": "yes"}, profiles_file)
    profile = get_profile("dev", profiles_file)
    assert profile == {"DEBUG": "0", "NEW_VAR": "yes"}


def test_delete_profile_existing(profiles_file):
    set_profile("temp", {"X": "1"}, profiles_file)
    result = delete_profile("temp", profiles_file)
    assert result is True
    assert get_profile("temp", profiles_file) is None


def test_delete_profile_missing(profiles_file):
    result = delete_profile("ghost", profiles_file)
    assert result is False


def test_list_profile_names(profiles_file):
    set_profile("zebra", {}, profiles_file)
    set_profile("alpha", {}, profiles_file)
    set_profile("mango", {}, profiles_file)
    names = list_profile_names(profiles_file)
    assert names == ["alpha", "mango", "zebra"]


def test_save_creates_parent_directories(tmp_path):
    nested = tmp_path / "a" / "b" / "profiles.json"
    save_profiles({"x": {"K": "V"}}, nested)
    assert nested.exists()
    assert json.loads(nested.read_text()) == {"x": {"K": "V"}}
