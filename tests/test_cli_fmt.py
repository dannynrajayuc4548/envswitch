"""Integration tests for the fmt CLI commands."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_fmt import fmt_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles():
    return {
        "dev": {"API_URL": "http://localhost", "DEBUG": "true"},
        "prod": {"API_URL": "https://example.com", "DEBUG": "false"},
    }


def test_fmt_show_table(runner, sample_profiles):
    with patch("envswitch.cli_fmt.load_profiles", return_value=sample_profiles):
        result = runner.invoke(fmt_cmd, ["show", "dev"])
    assert result.exit_code == 0
    assert "API_URL" in result.output
    assert "DEBUG" in result.output


def test_fmt_show_json(runner, sample_profiles):
    with patch("envswitch.cli_fmt.load_profiles", return_value=sample_profiles):
        result = runner.invoke(fmt_cmd, ["show", "dev", "--format", "json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert "dev" in parsed
    assert parsed["dev"]["DEBUG"] == "true"


def test_fmt_show_dotenv(runner, sample_profiles):
    with patch("envswitch.cli_fmt.load_profiles", return_value=sample_profiles):
        result = runner.invoke(fmt_cmd, ["show", "dev", "-f", "dotenv"])
    assert result.exit_code == 0
    assert "# Profile: dev" in result.output
    assert 'DEBUG="true"' in result.output


def test_fmt_show_yaml(runner, sample_profiles):
    with patch("envswitch.cli_fmt.load_profiles", return_value=sample_profiles):
        result = runner.invoke(fmt_cmd, ["show", "dev", "-f", "yaml"])
    assert result.exit_code == 0
    assert "dev:" in result.output


def test_fmt_show_profile_not_found(runner, sample_profiles):
    with patch("envswitch.cli_fmt.load_profiles", return_value=sample_profiles):
        result = runner.invoke(fmt_cmd, ["show", "missing"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_fmt_all_table(runner, sample_profiles):
    with patch("envswitch.cli_fmt.load_profiles", return_value=sample_profiles):
        result = runner.invoke(fmt_cmd, ["all"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_fmt_all_no_profiles(runner):
    with patch("envswitch.cli_fmt.load_profiles", return_value={}):
        result = runner.invoke(fmt_cmd, ["all"])
    assert result.exit_code == 0
    assert "No profiles" in result.output
