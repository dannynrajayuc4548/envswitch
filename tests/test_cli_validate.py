"""Tests for the validate CLI command."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_validate import validate_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles():
    return {
        "dev": {"API_URL": "http://localhost", "DEBUG": "true"},
        "prod": {"API_URL": "https://example.com", "DEBUG": "false"},
    }


def test_validate_all_profiles_valid(runner, sample_profiles):
    with patch("envswitch.cli_validate.load_profiles", return_value=sample_profiles):
        result = runner.invoke(validate_cmd, [])
    assert result.exit_code == 0
    assert "[OK]" in result.output
    assert "dev" in result.output
    assert "prod" in result.output


def test_validate_single_profile_valid(runner, sample_profiles):
    with patch("envswitch.cli_validate.load_profiles", return_value=sample_profiles):
        result = runner.invoke(validate_cmd, ["dev"])
    assert result.exit_code == 0
    assert "[OK]" in result.output
    assert "dev" in result.output


def test_validate_profile_not_found(runner, sample_profiles):
    with patch("envswitch.cli_validate.load_profiles", return_value=sample_profiles):
        result = runner.invoke(validate_cmd, ["staging"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_validate_no_profiles(runner):
    with patch("envswitch.cli_validate.load_profiles", return_value={}):
        result = runner.invoke(validate_cmd, [])
    assert result.exit_code == 0
    assert "No profiles found" in result.output


def test_validate_invalid_profile_exits_nonzero(runner):
    bad_profiles = {
        "bad name": {"123INVALID": "value"},
    }
    with patch("envswitch.cli_validate.load_profiles", return_value=bad_profiles):
        result = runner.invoke(validate_cmd, [])
    assert result.exit_code != 0
    assert "[INVALID]" in result.output


def test_validate_mixed_profiles(runner):
    mixed = {
        "good": {"KEY": "value"},
        "bad name": {"VALID_KEY": "val"},
    }
    with patch("envswitch.cli_validate.load_profiles", return_value=mixed):
        result = runner.invoke(validate_cmd, [])
    assert result.exit_code != 0
    assert "[OK]" in result.output
    assert "[INVALID]" in result.output
