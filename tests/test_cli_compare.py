"""Tests for CLI compare commands."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_compare import compare_cmd


SAMPLE = {
    "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
    "prod": {"DB_HOST": "prod.db", "SECRET": "abc"},
}


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles():
    with patch("envswitch.compare.load_profiles", return_value=SAMPLE):
        yield


def test_compare_show_two_profiles(runner, sample_profiles):
    result = runner.invoke(compare_cmd, ["show", "dev", "prod"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "dev" in result.output
    assert "prod" in result.output


def test_compare_show_missing_shown(runner, sample_profiles):
    result = runner.invoke(compare_cmd, ["show", "dev", "prod"])
    assert "(missing)" in result.output


def test_compare_show_raw(runner, sample_profiles):
    result = runner.invoke(compare_cmd, ["show", "--raw", "dev", "prod"])
    assert result.exit_code == 0
    assert "dev: DB_HOST=localhost" in result.output


def test_compare_show_profile_not_found(runner, sample_profiles):
    result = runner.invoke(compare_cmd, ["show", "dev", "ghost"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_compare_show_requires_two_profiles(runner, sample_profiles):
    result = runner.invoke(compare_cmd, ["show", "dev"])
    assert result.exit_code != 0
