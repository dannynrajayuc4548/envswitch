"""Tests for envswitch.compare module."""
import pytest
from unittest.mock import patch
from envswitch.compare import compare_profiles, format_compare, ProfileNotFoundError


SAMPLE = {
    "dev": {"DB_HOST": "localhost", "DEBUG": "true", "PORT": "5432"},
    "prod": {"DB_HOST": "prod.db", "DEBUG": "false", "SECRET": "xyz"},
    "staging": {"DB_HOST": "staging.db", "PORT": "5433"},
}


@pytest.fixture
def mock_load():
    with patch("envswitch.compare.load_profiles", return_value=SAMPLE) as m:
        yield m


def test_compare_all_keys_present(mock_load):
    result = compare_profiles(["dev", "prod"])
    assert set(result.keys()) == {"DB_HOST", "DEBUG", "PORT", "SECRET"}


def test_compare_missing_key_is_none(mock_load):
    result = compare_profiles(["dev", "prod"])
    assert result["SECRET"]["dev"] is None
    assert result["SECRET"]["prod"] == "xyz"


def test_compare_shared_key_values(mock_load):
    result = compare_profiles(["dev", "prod"])
    assert result["DB_HOST"]["dev"] == "localhost"
    assert result["DB_HOST"]["prod"] == "prod.db"


def test_compare_three_profiles(mock_load):
    result = compare_profiles(["dev", "prod", "staging"])
    assert "PORT" in result
    assert result["PORT"]["prod"] is None
    assert result["PORT"]["staging"] == "5433"


def test_compare_profile_not_found(mock_load):
    with pytest.raises(ProfileNotFoundError):
        compare_profiles(["dev", "nonexistent"])


def test_format_compare_contains_headers(mock_load):
    result = compare_profiles(["dev", "prod"])
    output = format_compare(result, ["dev", "prod"])
    assert "dev" in output
    assert "prod" in output
    assert "DB_HOST" in output


def test_format_compare_missing_shown(mock_load):
    result = compare_profiles(["dev", "prod"])
    output = format_compare(result, ["dev", "prod"])
    assert "(missing)" in output
