"""Tests for envswitch.encrypt module."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

pytest.importorskip("cryptography")

from envswitch.encrypt import (
    generate_key, save_key, load_key, encrypt_value, decrypt_value,
    is_encrypted, encrypt_profile, decrypt_profile, EncryptionError
)


@pytest.fixture
def key():
    return generate_key()


def test_generate_key_returns_bytes(key):
    assert isinstance(key, bytes)
    assert len(key) > 0


def test_encrypt_value_produces_enc_prefix(key):
    result = encrypt_value("secret", key)
    assert result.startswith("enc:")


def test_decrypt_value_roundtrip(key):
    original = "my_secret_value"
    encrypted = encrypt_value(original, key)
    assert decrypt_value(encrypted, key) == original


def test_decrypt_plaintext_passthrough(key):
    assert decrypt_value("plaintext", key) == "plaintext"


def test_decrypt_with_wrong_key(key):
    encrypted = encrypt_value("secret", key)
    wrong_key = generate_key()
    with pytest.raises(EncryptionError):
        decrypt_value(encrypted, wrong_key)


def test_is_encrypted_true(key):
    enc = encrypt_value("val", key)
    assert is_encrypted(enc) is True


def test_is_encrypted_false():
    assert is_encrypted("plainvalue") is False


def test_encrypt_profile_all_vars(key):
    profile = {"A": "foo", "B": "bar"}
    result = encrypt_profile(profile, key)
    assert is_encrypted(result["A"])
    assert is_encrypted(result["B"])


def test_encrypt_profile_selected_vars(key):
    profile = {"A": "foo", "B": "bar"}
    result = encrypt_profile(profile, key, vars_to_encrypt=["A"])
    assert is_encrypted(result["A"])
    assert not is_encrypted(result["B"])


def test_encrypt_profile_skips_already_encrypted(key):
    profile = {"A": "foo"}
    first = encrypt_profile(profile, key)
    second = encrypt_profile(first, key)
    assert first["A"] == second["A"]


def test_decrypt_profile(key):
    profile = {"A": "hello", "B": "world"}
    encrypted = encrypt_profile(profile, key)
    decrypted = decrypt_profile(encrypted, key)
    assert decrypted == profile


def test_save_and_load_key(tmp_path, key):
    key_file = tmp_path / "test.key"
    save_key(key, key_file)
    loaded = load_key(key_file)
    assert loaded == key


def test_load_key_missing_file(tmp_path):
    with pytest.raises(EncryptionError, match="No encryption key"):
        load_key(tmp_path / "nonexistent.key")
