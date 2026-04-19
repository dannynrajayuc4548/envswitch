"""Tests for envswitch.cli_encrypt commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path

pytest.importorskip("cryptography")

from envswitch.cli_encrypt import encrypt_cmd
from envswitch.encrypt import generate_key


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles():
    return {"dev": {"API_KEY": "abc123", "DEBUG": "true"}}


def test_enc_init_creates_key(runner, tmp_path):
    key_path = tmp_path / "encrypt.key"
    with patch("envswitch.cli_encrypt.get_key_path", return_value=key_path):
        result = runner.invoke(encrypt_cmd, ["init"])
    assert result.exit_code == 0
    assert "saved" in result.output
    assert key_path.exists()


def test_enc_init_refuses_overwrite_without_force(runner, tmp_path):
    key_path = tmp_path / "encrypt.key"
    key_path.write_bytes(generate_key())
    with patch("envswitch.cli_encrypt.get_key_path", return_value=key_path):
        result = runner.invoke(encrypt_cmd, ["init"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_enc_init_force_overwrites(runner, tmp_path):
    key_path = tmp_path / "encrypt.key"
    key_path.write_bytes(generate_key())
    with patch("envswitch.cli_encrypt.get_key_path", return_value=key_path):
        result = runner.invoke(encrypt_cmd, ["init", "--force"])
    assert result.exit_code == 0


def test_enc_encrypt_profile(runner, sample_profiles):
    key = generate_key()
    with patch("envswitch.cli_encrypt.load_key", return_value=key), \
         patch("envswitch.cli_encrypt.load_profiles", return_value=sample_profiles), \
         patch("envswitch.cli_encrypt.save_profiles") as mock_save:
        result = runner.invoke(encrypt_cmd, ["encrypt", "dev"])
    assert result.exit_code == 0
    assert "encrypted" in result.output
    saved = mock_save.call_args[0][0]
    from envswitch.encrypt import is_encrypted
    assert is_encrypted(saved["dev"]["API_KEY"])


def test_enc_encrypt_profile_not_found(runner):
    key = generate_key()
    with patch("envswitch.cli_encrypt.load_key", return_value=key), \
         patch("envswitch.cli_encrypt.load_profiles", return_value={}):
        result = runner.invoke(encrypt_cmd, ["encrypt", "missing"])
    assert result.exit_code != 0


def test_enc_status_shows_plaintext(runner, sample_profiles):
    with patch("envswitch.cli_encrypt.load_profiles", return_value=sample_profiles):
        result = runner.invoke(encrypt_cmd, ["status", "dev"])
    assert result.exit_code == 0
    assert "[plaintext]" in result.output


def test_enc_decrypt_shows_values(runner, sample_profiles):
    key = generate_key()
    from envswitch.encrypt import encrypt_profile
    encrypted_profiles = {"dev": encrypt_profile(sample_profiles["dev"], key)}
    with patch("envswitch.cli_encrypt.load_key", return_value=key), \
         patch("envswitch.cli_encrypt.load_profiles", return_value=encrypted_profiles):
        result = runner.invoke(encrypt_cmd, ["decrypt", "dev"])
    assert result.exit_code == 0
    assert "API_KEY=abc123" in result.output
