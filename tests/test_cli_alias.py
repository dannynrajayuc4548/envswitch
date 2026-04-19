"""Tests for envswitch CLI alias commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_alias import alias_cmd
from envswitch.alias import AliasError


SAMPLE_PROFILES = {"dev": {"X": "1"}, "prod": {"X": "0"}}


@pytest.fixture
def runner():
    return CliRunner()


def test_alias_add_success(runner):
    with patch("envswitch.alias.load_profiles", return_value=SAMPLE_PROFILES):
        with patch("envswitch.alias.save_aliases"):
            with patch("envswitch.alias.load_aliases", return_value={}):
                result = runner.invoke(alias_cmd, ["add", "d", "dev"])
    assert result.exit_code == 0
    assert "added" in result.output


def test_alias_add_profile_not_found(runner):
    with patch("envswitch.alias.load_profiles", return_value=SAMPLE_PROFILES):
        result = runner.invoke(alias_cmd, ["add", "x", "missing"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_alias_remove_success(runner):
    with patch("envswitch.alias.load_aliases", return_value={"d": "dev"}):
        with patch("envswitch.alias.save_aliases"):
            result = runner.invoke(alias_cmd, ["remove", "d"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_alias_remove_not_found(runner):
    with patch("envswitch.alias.load_aliases", return_value={}):
        result = runner.invoke(alias_cmd, ["remove", "ghost"])
    assert result.exit_code == 1


def test_alias_list_empty(runner):
    with patch("envswitch.alias.load_aliases", return_value={}):
        result = runner.invoke(alias_cmd, ["list"])
    assert "No aliases" in result.output


def test_alias_list_with_entries(runner):
    with patch("envswitch.alias.load_aliases", return_value={"d": "dev", "p": "prod"}):
        result = runner.invoke(alias_cmd, ["list"])
    assert "d -> dev" in result.output
    assert "p -> prod" in result.output


def test_alias_resolve_found(runner):
    with patch("envswitch.alias.load_aliases", return_value={"d": "dev"}):
        result = runner.invoke(alias_cmd, ["resolve", "d"])
    assert "dev" in result.output
    assert result.exit_code == 0


def test_alias_resolve_not_found(runner):
    with patch("envswitch.alias.load_aliases", return_value={}):
        result = runner.invoke(alias_cmd, ["resolve", "nope"])
    assert result.exit_code == 1
