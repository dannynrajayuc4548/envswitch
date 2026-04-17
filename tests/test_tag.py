"""Tests for envswitch.tag module."""
import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envswitch.tag import add_tag, remove_tag, get_tags, find_by_tag, load_tags, save_tags
from envswitch.cli_tag import tag_cmd

SAMPLE_PROFILES = {"dev": {"A": "1"}, "prod": {"A": "2"}, "staging": {"A": "3"}}


@pytest.fixture
def tag_file(tmp_path):
    return tmp_path / "tags.json"


def test_load_tags_missing_file(tag_file):
    assert load_tags(tag_file) == {}


def test_load_tags_invalid_json(tag_file):
    tag_file.write_text("not json")
    assert load_tags(tag_file) == {}


def test_save_and_load_tags(tag_file):
    data = {"dev": ["local", "debug"]}
    save_tags(data, tag_file)
    assert load_tags(tag_file) == data


def test_add_tag_success(tag_file):
    with patch("envswitch.tag.load_profiles", return_value=SAMPLE_PROFILES):
        add_tag("dev", "local", tag_file)
    assert "local" in load_tags(tag_file).get("dev", [])


def test_add_tag_profile_not_found(tag_file):
    with patch("envswitch.tag.load_profiles", return_value=SAMPLE_PROFILES):
        with pytest.raises(KeyError):
            add_tag("nonexistent", "mytag", tag_file)


def test_add_tag_no_duplicates(tag_file):
    with patch("envswitch.tag.load_profiles", return_value=SAMPLE_PROFILES):
        add_tag("dev", "local", tag_file)
        add_tag("dev", "local", tag_file)
    assert load_tags(tag_file)["dev"].count("local") == 1


def test_remove_tag(tag_file):
    save_tags({"dev": ["local", "debug"]}, tag_file)
    remove_tag("dev", "local", tag_file)
    assert "local" not in load_tags(tag_file).get("dev", [])


def test_find_by_tag(tag_file):
    save_tags({"dev": ["local"], "prod": ["live"], "staging": ["local"]}, tag_file)
    result = find_by_tag("local", tag_file)
    assert set(result) == {"dev", "staging"}


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_tag_add(runner, tag_file):
    with patch("envswitch.tag.load_profiles", return_value=SAMPLE_PROFILES):
        with patch("envswitch.tag.get_tags_path", return_value=tag_file):
            result = runner.invoke(tag_cmd, ["add", "dev", "local"])
    assert result.exit_code == 0
    assert "Tagged" in result.output


def test_cli_tag_find(runner, tag_file):
    save_tags({"dev": ["local"], "prod": ["live"]}, tag_file)
    with patch("envswitch.tag.get_tags_path", return_value=tag_file):
        result = runner.invoke(tag_cmd, ["find", "local"])
    assert "dev" in result.output
    assert "prod" not in result.output
