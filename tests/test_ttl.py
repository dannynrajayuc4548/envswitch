"""Unit tests for envswitch.ttl."""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from envswitch.ttl import (
    TTLError,
    get_expiry,
    is_expired,
    load_ttl,
    purge_expired,
    remove_ttl,
    save_ttl,
    set_ttl,
)


@pytest.fixture(autouse=True)
def ttl_file(tmp_path, monkeypatch):
    ttl_path = tmp_path / "ttl.json"
    monkeypatch.setattr("envswitch.ttl.get_ttl_path", lambda: ttl_path)
    return ttl_path


def test_load_ttl_missing_file():
    assert load_ttl() == {}


def test_load_ttl_invalid_json(ttl_file):
    ttl_file.write_text("not json")
    assert load_ttl() == {}


def test_save_and_load_ttl(ttl_file):
    data = {"dev": time.time() + 100}
    save_ttl(data)
    loaded = load_ttl()
    assert "dev" in loaded
    assert abs(loaded["dev"] - data["dev"]) < 0.01


def test_set_ttl_creates_entry():
    set_ttl("dev", 300)
    expiry = get_expiry("dev")
    assert expiry is not None
    assert expiry > time.time()


def test_set_ttl_negative_raises():
    with pytest.raises(TTLError):
        set_ttl("dev", -10)


def test_set_ttl_zero_raises():
    with pytest.raises(TTLError):
        set_ttl("dev", 0)


def test_remove_ttl():
    set_ttl("dev", 300)
    remove_ttl("dev")
    assert get_expiry("dev") is None


def test_remove_ttl_nonexistent_is_noop():
    remove_ttl("ghost")  # should not raise


def test_is_expired_false_for_future():
    set_ttl("dev", 9999)
    assert not is_expired("dev")


def test_is_expired_true_for_past():
    save_ttl({"dev": time.time() - 1})
    assert is_expired("dev")


def test_is_expired_false_for_no_ttl():
    assert not is_expired("no-such-profile")


def test_purge_expired_removes_profiles():
    profiles = {"dev": {"KEY": "val"}, "prod": {"KEY": "val"}}
    save_ttl({"dev": time.time() - 1, "prod": time.time() + 9999})
    purged = purge_expired(profiles)
    assert purged == ["dev"]
    assert "dev" not in profiles
    assert "prod" in profiles


def test_purge_expired_cleans_ttl_file():
    profiles = {"dev": {}}
    save_ttl({"dev": time.time() - 1})
    purge_expired(profiles)
    assert get_expiry("dev") is None
