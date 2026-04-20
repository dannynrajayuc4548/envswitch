"""Tests for envswitch.env_check."""

from unittest.mock import patch

import pytest

from envswitch.env_check import check_profiles, score_profile


SAMPLE_PROFILES = {
    "dev": {"APP_ENV": "development", "DEBUG": "true", "PORT": "8000"},
    "prod": {"APP_ENV": "production", "DEBUG": "false", "PORT": "80"},
    "staging": {"APP_ENV": "staging", "DEBUG": "false"},
    "empty": {},
}


def test_score_profile_exact_match():
    env = {"APP_ENV": "development", "DEBUG": "true", "PORT": "8000"}
    matching, total = score_profile(SAMPLE_PROFILES["dev"], env)
    assert matching == 3
    assert total == 3


def test_score_profile_partial_match():
    env = {"APP_ENV": "production", "DEBUG": "false", "PORT": "9999"}
    matching, total = score_profile(SAMPLE_PROFILES["prod"], env)
    assert matching == 2
    assert total == 3


def test_score_profile_no_match():
    env = {"UNRELATED": "value"}
    matching, total = score_profile(SAMPLE_PROFILES["dev"], env)
    assert matching == 0
    assert total == 3


def test_score_profile_empty_profile():
    env = {"APP_ENV": "development"}
    matching, total = score_profile({}, env)
    assert matching == 0
    assert total == 0


@patch("envswitch.env_check.load_profiles", return_value=SAMPLE_PROFILES)
def test_check_profiles_exact_match(mock_load):
    env = {"APP_ENV": "development", "DEBUG": "true", "PORT": "8000"}
    results = check_profiles(env=env, threshold=1.0)
    assert len(results) == 1
    assert results[0]["name"] == "dev"
    assert results[0]["exact"] is True


@patch("envswitch.env_check.load_profiles", return_value=SAMPLE_PROFILES)
def test_check_profiles_partial_threshold(mock_load):
    env = {"APP_ENV": "production", "DEBUG": "false", "PORT": "9999"}
    results = check_profiles(env=env, threshold=0.5)
    names = [r["name"] for r in results]
    assert "prod" in names  # 2/3 ≈ 0.67
    assert "staging" in names  # 1/2 = 0.5


@patch("envswitch.env_check.load_profiles", return_value=SAMPLE_PROFILES)
def test_check_profiles_sorted_by_ratio(mock_load):
    env = {"APP_ENV": "production", "DEBUG": "false", "PORT": "80"}
    results = check_profiles(env=env, threshold=0.0)
    ratios = [r["ratio"] for r in results]
    assert ratios == sorted(ratios, reverse=True)


@patch("envswitch.env_check.load_profiles", return_value=SAMPLE_PROFILES)
def test_check_profiles_empty_profile_excluded_at_threshold_1(mock_load):
    env = {"APP_ENV": "development"}
    results = check_profiles(env=env, threshold=1.0)
    names = [r["name"] for r in results]
    assert "empty" not in names


@patch("envswitch.env_check.load_profiles", return_value=SAMPLE_PROFILES)
def test_check_profiles_no_matches(mock_load):
    env = {"TOTALLY_UNRELATED": "xyz"}
    results = check_profiles(env=env, threshold=1.0)
    assert results == []
