"""Tests for envswitch.schedule."""

import json
import pytest
from datetime import datetime
from unittest.mock import patch
from pathlib import Path


@pytest.fixture
def schedule_file(tmp_path, monkeypatch):
    monkeypatch.setattr("envswitch.schedule.get_schedule_path", lambda: tmp_path / "schedules.json")
    return tmp_path / "schedules.json"


@pytest.fixture
def mock_profile(monkeypatch):
    monkeypatch.setattr("envswitch.schedule.get_profile", lambda name: {"KEY": "val"} if name == "work" else None)


def test_load_schedules_missing_file(schedule_file):
    from envswitch.schedule import load_schedules
    assert load_schedules() == {}


def test_load_schedules_invalid_json(schedule_file):
    from envswitch.schedule import load_schedules
    schedule_file.write_text("not json")
    assert load_schedules() == {}


def test_add_and_get_schedule(schedule_file, mock_profile):
    from envswitch.schedule import add_schedule, get_schedule
    add_schedule("work", "09:00", "17:00", ["monday", "friday"])
    sched = get_schedule("work")
    assert sched["start"] == "09:00"
    assert sched["end"] == "17:00"
    assert "monday" in sched["days"]


def test_add_schedule_profile_not_found(schedule_file, monkeypatch):
    from envswitch.schedule import add_schedule
    monkeypatch.setattr("envswitch.schedule.get_profile", lambda name: None)
    with pytest.raises(ValueError, match="not found"):
        add_schedule("ghost", "09:00", "17:00")


def test_add_schedule_invalid_time(schedule_file, mock_profile):
    from envswitch.schedule import add_schedule
    with pytest.raises(ValueError):
        add_schedule("work", "9am", "5pm")


def test_remove_schedule(schedule_file, mock_profile):
    from envswitch.schedule import add_schedule, remove_schedule, get_schedule
    add_schedule("work", "08:00", "16:00")
    remove_schedule("work")
    assert get_schedule("work") is None


def test_remove_schedule_not_found(schedule_file):
    from envswitch.schedule import remove_schedule
    with pytest.raises(KeyError):
        remove_schedule("nonexistent")


def test_get_active_profile_match(schedule_file, mock_profile):
    from envswitch.schedule import add_schedule, get_active_profile
    add_schedule("work", "08:00", "18:00")
    now = datetime(2024, 1, 1, 12, 0)  # Monday noon
    assert get_active_profile(now) == "work"


def test_get_active_profile_no_match(schedule_file, mock_profile):
    from envswitch.schedule import add_schedule, get_active_profile
    add_schedule("work", "08:00", "09:00")
    now = datetime(2024, 1, 1, 20, 0)
    assert get_active_profile(now) is None


def test_get_active_profile_day_filter(schedule_file, mock_profile):
    from envswitch.schedule import add_schedule, get_active_profile
    add_schedule("work", "08:00", "18:00", ["saturday"])
    now = datetime(2024, 1, 1, 12, 0)  # Monday
    assert get_active_profile(now) is None
