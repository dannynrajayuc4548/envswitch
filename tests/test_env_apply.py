"""Tests for envswitch.env_apply module."""

import pytest
from unittest.mock import patch
from envswitch.env_apply import apply_profile, write_apply_script, ProfileNotFoundError


SAMPLE_PROFILES = {
    "dev": {"API_URL": "http://localhost", "DEBUG": "true"},
    "prod": {"API_URL": "https://example.com", "SECRET": 'has"quote'},
}


@pytest.fixture
def mock_load():
    with patch("envswitch.env_apply.load_profiles", return_value=SAMPLE_PROFILES):
        with patch("envswitch.env_apply.abort_if_locked"):
            yield


def test_apply_bash_format(mock_load):
    result = apply_profile("dev", shell="bash")
    assert 'export API_URL="http://localhost"' in result
    assert 'export DEBUG="true"' in result


def test_apply_fish_format(mock_load):
    result = apply_profile("dev", shell="fish")
    assert 'set -x API_URL "http://localhost"' in result


def test_apply_powershell_format(mock_load):
    result = apply_profile("dev", shell="powershell")
    assert '$env:API_URL = "http://localhost"' in result


def test_apply_bash_escapes_quotes(mock_load):
    result = apply_profile("prod", shell="bash")
    assert 'has\\"quote' in result


def test_apply_powershell_escapes_quotes(mock_load):
    result = apply_profile("prod", shell="powershell")
    assert 'has`"quote' in result


def test_apply_profile_not_found(mock_load):
    with pytest.raises(ProfileNotFoundError):
        apply_profile("nonexistent")


def test_apply_unsupported_shell(mock_load):
    with pytest.raises(ValueError, match="Unsupported shell"):
        apply_profile("dev", shell="zsh")


def test_write_apply_script(mock_load, tmp_path):
    out = tmp_path / "env.sh"
    write_apply_script("dev", out, shell="bash")
    content = out.read_text()
    assert 'export API_URL="http://localhost"' in content
