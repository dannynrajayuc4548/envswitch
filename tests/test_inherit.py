"""Tests for profile inheritance."""

import pytest
from unittest.mock import patch

from envswitch.inherit import (
    resolve_profile,
    set_base,
    remove_base,
    get_resolved,
    ProfileNotFoundError,
    CircularInheritanceError,
)


SAMPLE = {
    "base": {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"},
    "dev": {"__base__": "base", "DEBUG": "true", "SECRET": "dev-secret"},
    "prod": {"__base__": "base", "HOST": "prod.example.com", "SECRET": "prod-secret"},
    "standalone": {"FOO": "bar"},
}


def test_resolve_no_base():
    result = resolve_profile("standalone", SAMPLE)
    assert result == {"FOO": "bar"}


def test_resolve_single_inheritance():
    result = resolve_profile("dev", SAMPLE)
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"
    assert result["DEBUG"] == "true"  # overridden
    assert result["SECRET"] == "dev-secret"
    assert "__base__" not in result


def test_resolve_override_in_child():
    result = resolve_profile("prod", SAMPLE)
    assert result["HOST"] == "prod.example.com"
    assert result["PORT"] == "5432"


def test_resolve_profile_not_found():
    with pytest.raises(ProfileNotFoundError):
        resolve_profile("missing", SAMPLE)


def test_resolve_base_not_found():
    profiles = {"child": {"__base__": "nonexistent", "X": "1"}}
    with pytest.raises(ProfileNotFoundError):
        resolve_profile("child", profiles)


def test_circular_inheritance():
    profiles = {
        "a": {"__base__": "b", "X": "1"},
        "b": {"__base__": "a", "Y": "2"},
    }
    with pytest.raises(CircularInheritanceError):
        resolve_profile("a", profiles)


def test_set_base_success():
    profiles = dict(SAMPLE)
    with patch("envswitch.inherit.load_profiles", return_value=dict(SAMPLE)), \
         patch("envswitch.inherit.save_profiles") as mock_save:
        set_base("standalone", "base")
        mock_save.assert_called_once()


def test_set_base_profile_not_found():
    with patch("envswitch.inherit.load_profiles", return_value=dict(SAMPLE)):
        with pytest.raises(ProfileNotFoundError):
            set_base("missing", "base")


def test_remove_base():
    profiles = {"dev": {"__base__": "base", "DEBUG": "true"}}
    with patch("envswitch.inherit.load_profiles", return_value=profiles), \
         patch("envswitch.inherit.save_profiles") as mock_save:
        remove_base("dev")
        assert "__base__" not in profiles["dev"]
        mock_save.assert_called_once()


def test_get_resolved():
    with patch("envswitch.inherit.load_profiles", return_value=dict(SAMPLE)):
        result = get_resolved("dev")
        assert result["HOST"] == "localhost"
        assert result["DEBUG"] == "true"
