"""Tests for the export module."""

import pytest
from envswitch.export import (
    export_bash,
    export_fish,
    export_powershell,
    export_dotenv,
    export_profile,
)

SAMPLE_VARS = {
    "API_KEY": "abc123",
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET": 'has"quote',
}


def test_export_bash_format():
    result = export_bash({"FOO": "bar", "BAZ": "qux"})
    assert 'export BAZ="qux"' in result
    assert 'export FOO="bar"' in result


def test_export_bash_escapes_quotes():
    result = export_bash({"KEY": 'val"ue'})
    assert 'export KEY="val\\"ue"' in result


def test_export_fish_format():
    result = export_fish({"FOO": "bar"})
    assert 'set -x FOO "bar"' in result


def test_export_fish_escapes_quotes():
    result = export_fish({"KEY": 'val"ue'})
    assert 'set -x KEY "val\\"ue"' in result


def test_export_powershell_format():
    result = export_powershell({"FOO": "bar"})
    assert '$env:FOO = "bar"' in result


def test_export_powershell_escapes_quotes():
    result = export_powershell({"KEY": 'val"ue'})
    assert '$env:KEY = "val`"ue"' in result


def test_export_dotenv_format():
    result = export_dotenv({"FOO": "bar"})
    assert 'FOO="bar"' in result


def test_export_dotenv_escapes_quotes():
    result = export_dotenv({"KEY": 'val"ue'})
    assert 'KEY="val\\"ue"' in result


def test_export_profile_bash():
    result = export_profile({"X": "1"}, shell="bash")
    assert 'export X="1"' in result


def test_export_profile_zsh():
    result = export_profile({"X": "1"}, shell="zsh")
    assert 'export X="1"' in result


def test_export_profile_fish():
    result = export_profile({"X": "1"}, shell="fish")
    assert 'set -x X "1"' in result


def test_export_profile_powershell():
    result = export_profile({"X": "1"}, shell="powershell")
    assert '$env:X = "1"' in result


def test_export_profile_dotenv_via_fmt():
    result = export_profile({"X": "1"}, fmt="dotenv")
    assert 'X="1"' in result


def test_export_profile_unsupported_shell():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_profile({"X": "1"}, shell="cmd")


def test_export_profile_sorted_keys():
    result = export_bash({"Z": "last", "A": "first"})
    assert result.index("A") < result.index("Z")
