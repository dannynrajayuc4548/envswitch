"""Tests for envswitch.diff module."""

import pytest
from envswitch.diff import diff_profiles, format_diff, ProfileNotFoundError


@pytest.fixture
def sample_profiles():
    return {
        "dev": {"APP_ENV": "development", "DB_HOST": "localhost", "DEBUG": "true"},
        "prod": {"APP_ENV": "production", "DB_HOST": "db.prod.example.com", "LOG_LEVEL": "warn"},
        "empty": {},
    }


def test_diff_added_vars(sample_profiles):
    result = diff_profiles("dev", "prod", sample_profiles)
    assert result["added"] == {"LOG_LEVEL": "warn"}


def test_diff_removed_vars(sample_profiles):
    result = diff_profiles("dev", "prod", sample_profiles)
    assert result["removed"] == {"DEBUG": "true"}


def test_diff_changed_vars(sample_profiles):
    result = diff_profiles("dev", "prod", sample_profiles)
    assert result["changed"] == {
        "APP_ENV": {"from": "development", "to": "production"},
        "DB_HOST": {"from": "localhost", "to": "db.prod.example.com"},
    }


def test_diff_unchanged_vars(sample_profiles):
    result = diff_profiles("dev", "dev", sample_profiles)
    assert result["added"] == {}
    assert result["removed"] == {}
    assert result["changed"] == {}
    assert result["unchanged"] == sample_profiles["dev"]


def test_diff_profile_a_not_found(sample_profiles):
    with pytest.raises(ProfileNotFoundError, match="'missing'"):
        diff_profiles("missing", "prod", sample_profiles)


def test_diff_profile_b_not_found(sample_profiles):
    with pytest.raises(ProfileNotFoundError, match="'ghost'"):
        diff_profiles("dev", "ghost", sample_profiles)


def test_diff_with_empty_profile(sample_profiles):
    result = diff_profiles("empty", "dev", sample_profiles)
    assert result["added"] == sample_profiles["dev"]
    assert result["removed"] == {}
    assert result["changed"] == {}
    assert result["unchanged"] == {}


def test_format_diff_lines(sample_profiles):
    result = diff_profiles("dev", "prod", sample_profiles)
    lines = format_diff(result)
    assert any(line.startswith("+") and "LOG_LEVEL" in line for line in lines)
    assert any(line.startswith("-") and "DEBUG" in line for line in lines)
    assert any(line.startswith("~") and "APP_ENV" in line for line in lines)


def test_format_diff_unchanged_indented(sample_profiles):
    result = diff_profiles("dev", "dev", sample_profiles)
    lines = format_diff(result)
    assert all(line.startswith("  ") for line in lines)
    assert len(lines) == len(sample_profiles["dev"])
