"""CLI tests for envswitch bookmark commands."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envswitch.cli_bookmark import bookmark_cmd


@pytest.fixture()
def runner():
    return CliRunner()


_PROFILES = {"dev": {"KEY": "val"}, "prod": {"KEY": "prodval"}}


@pytest.fixture()
def sample_bookmarks():
    return {
        "mydev": {"profile": "dev", "description": "local dev env"},
        "myprod": {"profile": "prod", "description": ""},
    }


def test_bookmark_add_success(runner):
    with patch("envswitch.bookmark.load_profiles", return_value=_PROFILES), \
         patch("envswitch.bookmark.load_bookmarks", return_value={}), \
         patch("envswitch.bookmark.save_bookmarks") as mock_save:
        result = runner.invoke(bookmark_cmd, ["add", "mydev", "dev", "-d", "local"])
    assert result.exit_code == 0
    assert "mydev" in result.output
    mock_save.assert_called_once()


def test_bookmark_add_profile_not_found(runner):
    with patch("envswitch.bookmark.load_profiles", return_value=_PROFILES):
        result = runner.invoke(bookmark_cmd, ["add", "bm", "staging"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_bookmark_add_duplicate_without_force(runner):
    existing = {"mydev": {"profile": "dev", "description": ""}}
    with patch("envswitch.bookmark.load_profiles", return_value=_PROFILES), \
         patch("envswitch.bookmark.load_bookmarks", return_value=existing):
        result = runner.invoke(bookmark_cmd, ["add", "mydev", "dev"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_bookmark_add_force_overwrites(runner):
    with patch("envswitch.bookmark.load_profiles", return_value=_PROFILES), \
         patch("envswitch.bookmark.load_bookmarks", return_value={}), \
         patch("envswitch.bookmark.save_bookmarks") as mock_save:
        result = runner.invoke(bookmark_cmd, ["add", "mydev", "dev", "--force"])
    assert result.exit_code == 0
    assert "saved" in result.output


def test_bookmark_remove_success(runner, sample_bookmarks):
    with patch("envswitch.bookmark.load_bookmarks", return_value=dict(sample_bookmarks)), \
         patch("envswitch.bookmark.save_bookmarks"):
        result = runner.invoke(bookmark_cmd, ["remove", "mydev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_bookmark_remove_not_found(runner):
    with patch("envswitch.bookmark.load_bookmarks", return_value={}):
        result = runner.invoke(bookmark_cmd, ["remove", "ghost"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_bookmark_show_existing(runner, sample_bookmarks):
    with patch("envswitch.bookmark.load_bookmarks", return_value=sample_bookmarks):
        result = runner.invoke(bookmark_cmd, ["show", "mydev"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "local dev env" in result.output


def test_bookmark_show_not_found(runner):
    with patch("envswitch.bookmark.load_bookmarks", return_value={}):
        result = runner.invoke(bookmark_cmd, ["show", "ghost"])
    assert result.exit_code != 0


def test_bookmark_list_empty(runner):
    with patch("envswitch.bookmark.load_bookmarks", return_value={}):
        result = runner.invoke(bookmark_cmd, ["list"])
    assert result.exit_code == 0
    assert "No bookmarks" in result.output


def test_bookmark_list_shows_all(runner, sample_bookmarks):
    with patch("envswitch.bookmark.load_bookmarks", return_value=sample_bookmarks):
        result = runner.invoke(bookmark_cmd, ["list"])
    assert result.exit_code == 0
    assert "mydev" in result.output
    assert "myprod" in result.output
