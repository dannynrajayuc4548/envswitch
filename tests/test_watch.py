"""Tests for envswitch.watch module."""
import pytest
from unittest.mock import patch, MagicMock
from envswitch.watch import ProfileWatcher, format_watch_diff


SAMPLE = {"KEY1": "val1", "KEY2": "val2"}
MODIFIED = {"KEY1": "changed", "KEY3": "new"}


def _make_watcher(profile_data, callback=None):
    cb = callback or MagicMock()
    with patch("envswitch.watch.load_profiles", return_value={"dev": profile_data}):
        w = ProfileWatcher("dev", cb, interval=0.01)
        w._last = dict(profile_data)
    return w, cb


def test_check_once_no_change():
    w, cb = _make_watcher(SAMPLE)
    with patch("envswitch.watch.load_profiles", return_value={"dev": dict(SAMPLE)}):
        changed = w.check_once()
    assert not changed
    cb.assert_not_called()


def test_check_once_detects_change():
    w, cb = _make_watcher(SAMPLE)
    with patch("envswitch.watch.load_profiles", return_value={"dev": dict(MODIFIED)}):
        changed = w.check_once()
    assert changed
    cb.assert_called_once()
    old, new = cb.call_args[0]
    assert old == SAMPLE
    assert new == MODIFIED


def test_check_once_missing_profile():
    w, cb = _make_watcher(SAMPLE)
    with patch("envswitch.watch.load_profiles", return_value={}):
        changed = w.check_once()
    assert not changed
    cb.assert_not_called()


def test_check_once_initialises_last_on_first_call():
    cb = MagicMock()
    w = ProfileWatcher("dev", cb, interval=0.01)
    with patch("envswitch.watch.load_profiles", return_value={"dev": dict(SAMPLE)}):
        changed = w.check_once()
    assert not changed
    assert w._last == SAMPLE


def test_format_watch_diff_added():
    result = format_watch_diff({}, {"A": "1"})
    assert "+ A=1" in result


def test_format_watch_diff_removed():
    result = format_watch_diff({"A": "1"}, {})
    assert "- A" in result


def test_format_watch_diff_changed():
    result = format_watch_diff({"A": "old"}, {"A": "new"})
    assert "~ A" in result
    assert "old" in result
    assert "new" in result


def test_format_watch_diff_no_changes():
    result = format_watch_diff({"A": "1"}, {"A": "1"})
    assert result == ""


def test_start_runs_limited_iterations():
    cb = MagicMock()
    w = ProfileWatcher("dev", cb, interval=0.0)
    calls = [{"dev": dict(SAMPLE)}, {"dev": dict(MODIFIED)}, {"dev": dict(MODIFIED)}]
    with patch("envswitch.watch.load_profiles", side_effect=calls):
        w.start(max_iterations=2)
    assert cb.call_count == 1
