"""Tests for envswitch.history module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envswitch.history import (
    load_history,
    save_history,
    record_switch,
    get_history,
    clear_history,
)


@pytest.fixture
def history_file(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


def test_load_history_missing_file(history_file: Path) -> None:
    assert load_history(history_file) == {}


def test_load_history_invalid_json(history_file: Path) -> None:
    history_file.write_text("not json")
    assert load_history(history_file) == {}


def test_load_history_invalid_format(history_file: Path) -> None:
    history_file.write_text(json.dumps(["not", "a", "dict"]))
    assert load_history(history_file) == {}


def test_save_and_load_history(history_file: Path) -> None:
    data = {"/home/user/project": [{"profile": "dev", "timestamp": "2024-01-01T00:00:00+00:00"}]}
    save_history(data, history_file)
    assert load_history(history_file) == data


def test_record_switch_creates_entry(history_file: Path) -> None:
    record_switch("dev", cwd="/project", path=history_file)
    entries = get_history(cwd="/project", path=history_file)
    assert len(entries) == 1
    assert entries[0]["profile"] == "dev"
    assert "timestamp" in entries[0]


def test_record_switch_multiple_entries(history_file: Path) -> None:
    record_switch("dev", cwd="/project", path=history_file)
    record_switch("staging", cwd="/project", path=history_file)
    entries = get_history(cwd="/project", path=history_file)
    assert len(entries) == 2
    assert entries[0]["profile"] == "dev"
    assert entries[1]["profile"] == "staging"


def test_record_switch_respects_max_entries(history_file: Path) -> None:
    for i in range(5):
        record_switch(f"profile{i}", cwd="/project", path=history_file, max_entries=3)
    entries = get_history(cwd="/project", path=history_file)
    assert len(entries) == 3
    assert entries[-1]["profile"] == "profile4"


def test_get_history_empty_for_unknown_dir(history_file: Path) -> None:
    assert get_history(cwd="/nonexistent", path=history_file) == []


def test_clear_history_specific_dir(history_file: Path) -> None:
    record_switch("dev", cwd="/project", path=history_file)
    record_switch("prod", cwd="/other", path=history_file)
    clear_history(cwd="/project", path=history_file)
    assert get_history(cwd="/project", path=history_file) == []
    assert len(get_history(cwd="/other", path=history_file)) == 1


def test_clear_history_all(history_file: Path) -> None:
    record_switch("dev", cwd="/project", path=history_file)
    record_switch("prod", cwd="/other", path=history_file)
    clear_history(cwd=None, path=history_file)
    assert load_history(history_file) == {}
