"""Unit tests for envswitch.fmt module."""

import json
import pytest
from envswitch.fmt import (
    format_as_table,
    format_as_json,
    format_as_dotenv,
    format_as_yaml,
    format_profile,
)


SAMPLE = {"API_KEY": "abc123", "DEBUG": "true"}


def test_format_as_table_contains_keys():
    out = format_as_table("dev", SAMPLE)
    assert "API_KEY" in out
    assert "abc123" in out
    assert "DEBUG" in out


def test_format_as_table_shows_profile_name():
    out = format_as_table("staging", SAMPLE)
    assert "staging" in out


def test_format_as_table_empty_profile():
    out = format_as_table("empty", {})
    assert "no variables" in out.lower()


def test_format_as_json_valid():
    out = format_as_json("dev", SAMPLE)
    parsed = json.loads(out)
    assert parsed == {"dev": SAMPLE}


def test_format_as_json_sorted_keys():
    out = format_as_json("dev", SAMPLE)
    assert "API_KEY" in out
    assert "DEBUG" in out


def test_format_as_dotenv_format():
    out = format_as_dotenv("dev", {"FOO": "bar"})
    assert 'FOO="bar"' in out
    assert "# Profile: dev" in out


def test_format_as_dotenv_escapes_quotes():
    out = format_as_dotenv("dev", {"MSG": 'say "hello"'})
    assert '\\"' in out


def test_format_as_yaml_format():
    out = format_as_yaml("dev", {"FOO": "bar"})
    assert "dev:" in out
    assert '  FOO: "bar"' in out


def test_format_profile_dispatches_table():
    out = format_profile("dev", SAMPLE, fmt="table")
    assert "API_KEY" in out


def test_format_profile_dispatches_json():
    out = format_profile("dev", SAMPLE, fmt="json")
    parsed = json.loads(out)
    assert "dev" in parsed


def test_format_profile_dispatches_dotenv():
    out = format_profile("dev", {"X": "1"}, fmt="dotenv")
    assert 'X="1"' in out


def test_format_profile_dispatches_yaml():
    out = format_profile("dev", {"X": "1"}, fmt="yaml")
    assert "dev:" in out


def test_format_profile_invalid_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        format_profile("dev", SAMPLE, fmt="xml")
