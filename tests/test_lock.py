"""Tests for envswitch.lock."""

import pytest
from pathlib import Path
from unittest.mock import patch
from envswitch.lock import (
    load_locks,
    save_locks,
    lock_profile,
    unlock_profile,
    is_locked,
    get_locked_profiles,
)


@pytest.fixture
def lock_file(tmp_path, monkeypatch):
    path = tmp_path / "locks.json"
    monkeypatch.setattr("envswitch.lock.get_lock_path", lambda: path)
    return path


def test_load_locks_missing_file(lock_file):
    assert load_locks() == []


def test_load_locks_invalid_json(lock_file):
    lock_file.write_text("not json")
    assert load_locks() == []


def test_load_locks_invalid_format(lock_file):
    lock_file.write_text('{"bad": true}')
    assert load_locks() == []


def test_save_and_load_locks(lock_file):
    save_locks(["prod", "staging"])
    assert load_locks() == ["prod", "staging"]


def test_lock_profile_adds_entry(lock_file):
    lock_profile("prod")
    assert "prod" in load_locks()


def test_lock_profile_no_duplicate(lock_file):
    lock_profile("prod")
    lock_profile("prod")
    assert load_locks().count("prod") == 1


def test_unlock_profile_removes_entry(lock_file):
    save_locks(["prod", "dev"])
    unlock_profile("prod")
    assert "prod" not in load_locks()
    assert "dev" in load_locks()


def test_unlock_profile_not_locked(lock_file):
    save_locks(["dev"])
    unlock_profile("prod")  # should not raise
    assert load_locks() == ["dev"]


def test_is_locked_true(lock_file):
    save_locks(["prod"])
    assert is_locked("prod") is True


def test_is_locked_false(lock_file):
    save_locks(["dev"])
    assert is_locked("prod") is False


def test_get_locked_profiles(lock_file):
    save_locks(["prod", "staging"])
    assert get_locked_profiles() == ["prod", "staging"]
