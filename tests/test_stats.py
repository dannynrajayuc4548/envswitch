"""Tests for envswitch.stats."""

import pytest
from unittest.mock import patch

from envswitch.stats import count_switches, most_used, audit_event_summary, profile_last_used, StatsError


SAMPLE_HISTORY = {
    "entries": [
        {"profile": "dev", "timestamp": "2024-01-01T10:00:00"},
        {"profile": "prod", "timestamp": "2024-01-02T11:00:00"},
        {"profile": "dev", "timestamp": "2024-01-03T12:00:00"},
        {"profile": "staging", "timestamp": "2024-01-04T13:00:00"},
        {"profile": "dev", "timestamp": "2024-01-05T14:00:00"},
    ]
}

SAMPLE_AUDIT = {
    "entries": [
        {"event": "set", "profile": "dev"},
        {"event": "delete", "profile": "old"},
        {"event": "set", "profile": "prod"},
        {"event": "lock", "profile": "prod"},
        {"event": "set", "profile": "staging"},
    ]
}


@patch("envswitch.stats.load_history", return_value=SAMPLE_HISTORY)
def test_count_switches_all(mock_hist):
    result = count_switches()
    assert result["dev"] == 3
    assert result["prod"] == 1
    assert result["staging"] == 1


@patch("envswitch.stats.load_history", return_value=SAMPLE_HISTORY)
def test_count_switches_specific_profile(mock_hist):
    result = count_switches("dev")
    assert result == {"dev": 3}


@patch("envswitch.stats.load_history", return_value=SAMPLE_HISTORY)
def test_count_switches_missing_profile_returns_zero(mock_hist):
    result = count_switches("nonexistent")
    assert result == {"nonexistent": 0}


@patch("envswitch.stats.load_history", return_value={"entries": "bad"})
def test_count_switches_malformed_raises(mock_hist):
    with pytest.raises(StatsError):
        count_switches()


@patch("envswitch.stats.load_history", return_value=SAMPLE_HISTORY)
def test_most_used_returns_top_n(mock_hist):
    result = most_used(top_n=2)
    assert len(result) == 2
    assert result[0]["profile"] == "dev"
    assert result[0]["count"] == 3


@patch("envswitch.stats.load_history", return_value=SAMPLE_HISTORY)
def test_most_used_default_top5(mock_hist):
    result = most_used()
    assert len(result) <= 5


@patch("envswitch.stats.load_audit", return_value=SAMPLE_AUDIT)
def test_audit_event_summary(mock_audit):
    result = audit_event_summary()
    assert result["set"] == 3
    assert result["delete"] == 1
    assert result["lock"] == 1


@patch("envswitch.stats.load_audit", return_value={"entries": 42})
def test_audit_event_summary_malformed_raises(mock_audit):
    with pytest.raises(StatsError):
        audit_event_summary()


@patch("envswitch.stats.load_history", return_value=SAMPLE_HISTORY)
def test_profile_last_used_returns_latest(mock_hist):
    result = profile_last_used("dev")
    assert result == "2024-01-05T14:00:00"


@patch("envswitch.stats.load_history", return_value=SAMPLE_HISTORY)
def test_profile_last_used_unknown_profile(mock_hist):
    result = profile_last_used("unknown")
    assert result is None
