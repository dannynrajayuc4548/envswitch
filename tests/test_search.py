"""Tests for envswitch.search module."""

import json
import pytest
from unittest.mock import patch

from envswitch.search import search_profiles, search_in_profile

SAMPLE_PROFILES = {
    "dev": {
        "DATABASE_URL": "postgres://localhost/dev",
        "DEBUG": "true",
        "API_KEY": "dev-secret",
    },
    "prod": {
        "DATABASE_URL": "postgres://prod-host/app",
        "DEBUG": "false",
        "API_KEY": "prod-secret",
    },
    "staging": {
        "CACHE_HOST": "redis://staging",
        "LOG_LEVEL": "info",
    },
}


@pytest.fixture(autouse=True)
def mock_load(monkeypatch):
    monkeypatch.setattr("envswitch.search.load_profiles", lambda: SAMPLE_PROFILES)


def test_search_profiles_by_key():
    results = search_profiles("DATABASE", search_values=False)
    assert "dev" in results
    assert "prod" in results
    assert "staging" not in results
    assert any(k == "DATABASE_URL" for k, v in results["dev"])


def test_search_profiles_by_value():
    results = search_profiles("secret", search_keys=False)
    assert "dev" in results
    assert "prod" in results
    assert "staging" not in results


def test_search_profiles_case_insensitive():
    results = search_profiles("debug", search_values=False)
    assert "dev" in results
    assert "prod" in results


def test_search_profiles_case_sensitive_no_match():
    results = search_profiles("debug", search_values=False, case_sensitive=True)
    assert len(results) == 0


def test_search_profiles_case_sensitive_match():
    results = search_profiles("DEBUG", search_values=False, case_sensitive=True)
    assert "dev" in results
    assert "prod" in results


def test_search_profiles_no_match():
    results = search_profiles("NONEXISTENT_VAR")
    assert results == {}


def test_search_profiles_value_match_across_profiles():
    results = search_profiles("false", search_keys=False)
    assert "prod" in results
    assert any(v == "false" for k, v in results["prod"])


def test_search_in_profile_found():
    matches = search_in_profile("dev", "KEY", search_values=False)
    assert ("API_KEY", "dev-secret") in matches


def test_search_in_profile_not_found_profile():
    with pytest.raises(KeyError, match="Profile 'unknown' not found"):
        search_in_profile("unknown", "anything")


def test_search_in_profile_no_match():
    matches = search_in_profile("staging", "DATABASE", search_values=False)
    assert matches == []


def test_search_in_profile_value_match():
    matches = search_in_profile("staging", "redis", search_keys=False)
    assert ("CACHE_HOST", "redis://staging") in matches
