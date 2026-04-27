"""Tests for envswitch.hotkey."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from envswitch import hotkey as hk
from envswitch.hotkey import (
    HotkeyError,
    bind_hotkey,
    list_hotkeys,
    load_hotkeys,
    resolve_hotkey,
    unbind_hotkey,
)


SAMPLE_PROFILES = {
    "dev": {"DB_HOST": "localhost"},
    "prod": {"DB_HOST": "prod.db.example.com"},
}


@pytest.fixture(autouse=True)
def patch_paths(tmp_path):
    hotkeys_file = tmp_path / "hotkeys.json"
    with (
        patch("envswitch.hotkey.get_hotkeys_path", return_value=hotkeys_file),
        patch("envswitch.hotkey.load_profiles", return_value=SAMPLE_PROFILES),
    ):
        yield hotkeys_file


def test_load_hotkeys_missing_file():
    result = load_hotkeys()
    assert result == {}


def test_load_hotkeys_invalid_json(patch_paths):
    patch_paths.write_text("not-json")
    assert load_hotkeys() == {}


def test_load_hotkeys_invalid_format(patch_paths):
    patch_paths.write_text(json.dumps(["list", "not", "dict"]))
    assert load_hotkeys() == {}


def test_bind_hotkey_success(patch_paths):
    bind_hotkey("ctrl+1", "dev")
    data = json.loads(patch_paths.read_text())
    assert data["ctrl+1"] == "dev"


def test_bind_hotkey_profile_not_found():
    with pytest.raises(HotkeyError, match="not found"):
        bind_hotkey("ctrl+9", "nonexistent")


def test_bind_hotkey_overwrites_existing(patch_paths):
    bind_hotkey("ctrl+1", "dev")
    bind_hotkey("ctrl+1", "prod")
    assert load_hotkeys()["ctrl+1"] == "prod"


def test_unbind_hotkey_success(patch_paths):
    bind_hotkey("ctrl+2", "prod")
    unbind_hotkey("ctrl+2")
    assert "ctrl+2" not in load_hotkeys()


def test_unbind_hotkey_not_bound():
    with pytest.raises(HotkeyError, match="not bound"):
        unbind_hotkey("ctrl+99")


def test_resolve_hotkey_returns_profile(patch_paths):
    bind_hotkey("ctrl+3", "dev")
    assert resolve_hotkey("ctrl+3") == "dev"


def test_resolve_hotkey_unbound_returns_none():
    assert resolve_hotkey("ctrl+99") is None


def test_list_hotkeys_returns_all(patch_paths):
    bind_hotkey("ctrl+1", "dev")
    bind_hotkey("ctrl+2", "prod")
    result = list_hotkeys()
    assert result == {"ctrl+1": "dev", "ctrl+2": "prod"}
