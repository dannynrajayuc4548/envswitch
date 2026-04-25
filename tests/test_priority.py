"""Unit tests for envswitch.priority."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from envswitch.priority import (
    PriorityError,
    get_priority,
    list_by_priority,
    load_priorities,
    remove_priority,
    save_priorities,
    set_priority,
)

SAMPLE_PROFILES = {
    "dev": {"DB_HOST": "localhost"},
    "prod": {"DB_HOST": "prod.example.com"},
    "staging": {"DB_HOST": "staging.example.com"},
}


@pytest.fixture()
def priority_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    pfile = tmp_path / "priorities.json"
    monkeypatch.setattr("envswitch.priority.get_priority_path", lambda: pfile)
    monkeypatch.setattr("envswitch.priority.load_profiles", lambda: SAMPLE_PROFILES)
    return pfile


def test_load_priorities_missing_file(priority_file: Path):
    assert load_priorities() == {}


def test_load_priorities_invalid_json(priority_file: Path):
    priority_file.write_text("not-json")
    assert load_priorities() == {}


def test_load_priorities_invalid_format(priority_file: Path):
    priority_file.write_text(json.dumps(["not", "a", "dict"]))
    assert load_priorities() == {}


def test_save_and_load_priorities(priority_file: Path):
    save_priorities({"dev": 10, "prod": 99})
    result = load_priorities()
    assert result == {"dev": 10, "prod": 99}


def test_set_priority_success(priority_file: Path):
    set_priority("dev", 5)
    assert get_priority("dev") == 5


def test_set_priority_profile_not_found(priority_file: Path):
    with pytest.raises(PriorityError, match="not found"):
        set_priority("nonexistent", 1)


def test_remove_priority_success(priority_file: Path):
    set_priority("prod", 20)
    remove_priority("prod")
    assert get_priority("prod") is None


def test_remove_priority_not_set(priority_file: Path):
    with pytest.raises(PriorityError, match="No priority set"):
        remove_priority("dev")


def test_get_priority_missing(priority_file: Path):
    assert get_priority("dev") is None


def test_list_by_priority_sorted(priority_file: Path):
    set_priority("dev", 5)
    set_priority("prod", 99)
    set_priority("staging", 42)
    result = list_by_priority()
    names = [name for name, _ in result]
    assert names == ["prod", "staging", "dev"]


def test_list_by_priority_empty(priority_file: Path):
    assert list_by_priority() == []
