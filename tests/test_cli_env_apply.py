"""Tests for envswitch.cli_env_apply CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_env_apply import apply_cmd
from envswitch.env_apply import ProfileNotFoundError


@pytest.fixture
def runner():
    return CliRunner()


SAMPLE_PROFILES = {
    "dev": {"API_URL": "http://localhost", "DEBUG": "true"},
}


def test_apply_print_bash(runner):
    with patch("envswitch.env_apply.load_profiles", return_value=SAMPLE_PROFILES):
        with patch("envswitch.env_apply.abort_if_locked"):
            result = runner.invoke(apply_cmd, ["print", "dev", "--shell", "bash"])
    assert result.exit_code == 0
    assert 'export API_URL="http://localhost"' in result.output


def test_apply_print_fish(runner):
    with patch("envswitch.env_apply.load_profiles", return_value=SAMPLE_PROFILES):
        with patch("envswitch.env_apply.abort_if_locked"):
            result = runner.invoke(apply_cmd, ["print", "dev", "--shell", "fish"])
    assert result.exit_code == 0
    assert 'set -x API_URL' in result.output


def test_apply_print_not_found(runner):
    with patch("envswitch.env_apply.load_profiles", return_value=SAMPLE_PROFILES):
        with patch("envswitch.env_apply.abort_if_locked"):
            result = runner.invoke(apply_cmd, ["print", "missing"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_apply_write_creates_file(runner, tmp_path):
    out = str(tmp_path / "env.sh")
    with patch("envswitch.env_apply.load_profiles", return_value=SAMPLE_PROFILES):
        with patch("envswitch.env_apply.abort_if_locked"):
            result = runner.invoke(apply_cmd, ["write", "dev", out, "--shell", "bash"])
    assert result.exit_code == 0
    assert "Script written" in result.output
    with open(out) as f:
        content = f.read()
    assert 'export API_URL' in content
