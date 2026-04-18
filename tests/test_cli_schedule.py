"""Tests for CLI schedule commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_schedule import schedule_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles():
    return {"work": {"ENV": "prod"}, "dev": {"ENV": "dev"}}


def test_sched_add_success(runner, sample_profiles):
    with patch("envswitch.schedule.load_schedules", return_value={}) as _ls, \
         patch("envswitch.schedule.save_schedules") as _ss, \
         patch("envswitch.schedule.get_profile", return_value={"ENV": "prod"}):
        result = runner.invoke(schedule_cmd, ["add", "work", "--start", "09:00", "--end", "17:00"])
        assert result.exit_code == 0
        assert "Schedule added" in result.output


def test_sched_add_profile_not_found(runner):
    with patch("envswitch.schedule.get_profile", return_value=None):
        result = runner.invoke(schedule_cmd, ["add", "ghost", "--start", "09:00", "--end", "17:00"])
        assert result.exit_code == 1
        assert "not found" in result.output


def test_sched_remove_success(runner):
    with patch("envswitch.schedule.load_schedules", return_value={"work": {"start": "09:00", "end": "17:00", "days": []}}), \
         patch("envswitch.schedule.save_schedules"):
        result = runner.invoke(schedule_cmd, ["remove", "work"])
        assert result.exit_code == 0
        assert "removed" in result.output


def test_sched_remove_not_found(runner):
    with patch("envswitch.schedule.load_schedules", return_value={}):
        result = runner.invoke(schedule_cmd, ["remove", "ghost"])
        assert result.exit_code == 1


def test_sched_list_empty(runner):
    with patch("envswitch.schedule.load_schedules", return_value={}):
        result = runner.invoke(schedule_cmd, ["list"])
        assert "No schedules" in result.output


def test_sched_list_with_entries(runner):
    schedules = {"work": {"start": "09:00", "end": "17:00", "days": ["monday"]}}
    with patch("envswitch.schedule.load_schedules", return_value=schedules):
        result = runner.invoke(schedule_cmd, ["list"])
        assert "work" in result.output
        assert "09:00" in result.output


def test_sched_active_found(runner):
    with patch("envswitch.schedule.get_active_profile", return_value="work"):
        result = runner.invoke(schedule_cmd, ["active"])
        assert "work" in result.output


def test_sched_active_none(runner):
    with patch("envswitch.schedule.get_active_profile", return_value=None):
        result = runner.invoke(schedule_cmd, ["active"])
        assert "No profile" in result.output
