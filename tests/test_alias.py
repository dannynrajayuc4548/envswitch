"""Tests for envswitch.alias module."""

import pytest
from pathlib import Path
from unittest.mock import patch
from envswitch.alias import add_alias, remove_alias, resolve_alias, list_aliases, AliasError


SAMPLE_PROFILES = {
    "dev": {"DEBUG": "true"},
    "prod": {"DEBUG": "false"},
}


@pytest.fixture
alias_file(tmp_path):
    return tmp_path / "aliases.json"


@pytest.fixture
def alias_file(tmp_path):
    return tmp_path / "aliases.json"


def test_add_alias_success(alias_file):
    with patch("envswitch.alias.load_profiles", return_value=SAMPLE_PROFILES):
        add_alias("d", "dev", path=alias_file)
    aliases = list_aliases(alias_file)
    assert aliases["d"] == "dev"


def test_add_alias_profile_not_found(alias_file):
    with patch("envswitch.alias.load_profiles", return_value=SAMPLE_PROFILES):
        with pytest.raises(AliasError, match="not found"):
            add_alias("x", "missing", path=alias_file)


def test_add_alias_duplicate(alias_file):
    with patch("envswitch.alias.load_profiles", return_value=SAMPLE_PROFILES):
        add_alias("d", "dev", path=alias_file)
        with pytest.raises(AliasError, match="already exists"):
            add_alias("d", "prod", path=alias_file)


def test_remove_alias_success(alias_file):
    with patch("envswitch.alias.load_profiles", return_value=SAMPLE_PROFILES):
        add_alias("d", "dev", path=alias_file)
    remove_alias("d", path=alias_file)
    assert list_aliases(alias_file) == {}


def test_remove_alias_not_found(alias_file):
    with pytest.raises(AliasError, match="not found"):
        remove_alias("ghost", path=alias_file)


def test_resolve_alias_existing(alias_file):
    with patch("envswitch.alias.load_profiles", return_value=SAMPLE_PROFILES):
        add_alias("p", "prod", path=alias_file)
    assert resolve_alias("p", path=alias_file) == "prod"


def test_resolve_alias_missing(alias_file):
    assert resolve_alias("nope", path=alias_file) is None


def test_list_aliases_empty(alias_file):
    assert list_aliases(alias_file) == {}


def test_list_aliases_multiple(alias_file):
    with patch("envswitch.alias.load_profiles", return_value=SAMPLE_PROFILES):
        add_alias("d", "dev", path=alias_file)
        add_alias("p", "prod", path=alias_file)
    aliases = list_aliases(alias_file)
    assert len(aliases) == 2
