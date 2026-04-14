"""Tests for the export CLI command."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_export import export_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles():
    return {
        "dev": {"API_KEY": "dev-key", "DEBUG": "true"},
        "prod": {"API_KEY": "prod-key", "DEBUG": "false"},
        "empty": {},
    }


def test_export_bash_default(runner, sample_profiles):
    with patch("envswitch.cli_export.load_profiles", return_value=sample_profiles):
        result = runner.invoke(export_cmd, ["dev"])
    assert result.exit_code == 0
    assert 'export API_KEY="dev-key"' in result.output
    assert 'export DEBUG="true"' in result.output


def test_export_fish_shell(runner, sample_profiles):
    with patch("envswitch.cli_export.load_profiles", return_value=sample_profiles):
        result = runner.invoke(export_cmd, ["dev", "--shell", "fish"])
    assert result.exit_code == 0
    assert 'set -x API_KEY "dev-key"' in result.output


def test_export_powershell_shell(runner, sample_profiles):
    with patch("envswitch.cli_export.load_profiles", return_value=sample_profiles):
        result = runner.invoke(export_cmd, ["prod", "--shell", "powershell"])
    assert result.exit_code == 0
    assert '$env:API_KEY = "prod-key"' in result.output


def test_export_dotenv_shell(runner, sample_profiles):
    with patch("envswitch.cli_export.load_profiles", return_value=sample_profiles):
        result = runner.invoke(export_cmd, ["dev", "--shell", "dotenv"])
    assert result.exit_code == 0
    assert 'API_KEY="dev-key"' in result.output


def test_export_missing_profile(runner, sample_profiles):
    with patch("envswitch.cli_export.load_profiles", return_value=sample_profiles):
        result = runner.invoke(export_cmd, ["nonexistent"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_export_empty_profile(runner, sample_profiles):
    with patch("envswitch.cli_export.load_profiles", return_value=sample_profiles):
        result = runner.invoke(export_cmd, ["empty"])
    assert result.exit_code != 0
    assert "no variables" in result.output


def test_export_to_file(runner, sample_profiles, tmp_path):
    out_file = tmp_path / "env_export.sh"
    with patch("envswitch.cli_export.load_profiles", return_value=sample_profiles):
        result = runner.invoke(export_cmd, ["dev", "--output", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert 'export API_KEY="dev-key"' in content


def test_export_zsh_same_as_bash(runner, sample_profiles):
    with patch("envswitch.cli_export.load_profiles", return_value=sample_profiles):
        bash_result = runner.invoke(export_cmd, ["dev", "--shell", "bash"])
        zsh_result = runner.invoke(export_cmd, ["dev", "--shell", "zsh"])
    assert bash_result.output == zsh_result.output
