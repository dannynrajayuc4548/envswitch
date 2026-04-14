"""Tests for envswitch.validate module."""

import pytest
from envswitch.validate import (
    validate_var_name,
    validate_var_value,
    validate_profile_name,
    validate_profile,
    validate_and_raise,
    ValidationError,
)


def test_validate_var_name_valid():
    assert validate_var_name("MY_VAR") is True
    assert validate_var_name("_PRIVATE") is True
    assert validate_var_name("var123") is True


def test_validate_var_name_invalid():
    assert validate_var_name("123VAR") is False
    assert validate_var_name("MY-VAR") is False
    assert validate_var_name("") is False
    assert validate_var_name("MY VAR") is False


def test_validate_var_value_valid():
    assert validate_var_value("hello") is True
    assert validate_var_value("") is True
    assert validate_var_value("has spaces") is True


def test_validate_var_value_invalid():
    assert validate_var_value(123) is False
    assert validate_var_value(None) is False
    assert validate_var_value(["list"]) is False


def test_validate_profile_name_valid():
    assert validate_profile_name("production") is True
    assert validate_profile_name("my-profile") is True
    assert validate_profile_name("profile_1") is True


def test_validate_profile_name_invalid():
    assert validate_profile_name("") is False
    assert validate_profile_name("has space") is False
    assert validate_profile_name("tab\there") is False


def test_validate_profile_no_errors():
    errors = validate_profile("dev", {"API_KEY": "abc123", "DEBUG": "true"})
    assert errors == []


def test_validate_profile_bad_var_name():
    errors = validate_profile("dev", {"123BAD": "value"})
    assert any("123BAD" in e for e in errors)


def test_validate_profile_bad_profile_name():
    errors = validate_profile("bad name", {"KEY": "val"})
    assert any("profile name" in e for e in errors)


def test_validate_profile_non_string_value():
    errors = validate_profile("dev", {"PORT": 8080})
    assert any("PORT" in e for e in errors)


def test_validate_profile_non_dict_variables():
    errors = validate_profile("dev", ["not", "a", "dict"])
    assert any("dictionary" in e for e in errors)


def test_validate_and_raise_valid():
    # Should not raise
    validate_and_raise("prod", {"KEY": "value"})


def test_validate_and_raise_invalid():
    with pytest.raises(ValidationError) as exc_info:
        validate_and_raise("bad name", {"123BAD": 99})
    assert len(exc_info.value.errors) >= 2
