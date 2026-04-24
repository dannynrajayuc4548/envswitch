"""Unit tests for envswitch.bookmark."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envswitch.bookmark import (
    BookmarkError,
    add_bookmark,
    get_bookmark,
    list_bookmarks,
    load_bookmarks,
    remove_bookmark,
    save_bookmarks,
)


@pytest.fixture()
def bookmark_file(tmp_path):
    return tmp_path / "bookmarks.json"


_PROFILES = {"dev": {"KEY": "val"}, "prod": {"KEY": "prodval"}}


def test_load_bookmarks_missing_file(bookmark_file):
    assert load_bookmarks(bookmark_file) == {}


def test_load_bookmarks_invalid_json(bookmark_file):
    bookmark_file.write_text("not json")
    assert load_bookmarks(bookmark_file) == {}


def test_load_bookmarks_invalid_format(bookmark_file):
    bookmark_file.write_text(json.dumps(["a", "b"]))
    assert load_bookmarks(bookmark_file) == {}


def test_save_and_load_bookmarks(bookmark_file):
    data = {"mybm": {"profile": "dev", "description": "local dev"}}
    save_bookmarks(data, bookmark_file)
    loaded = load_bookmarks(bookmark_file)
    assert loaded == data


def test_add_bookmark_success(bookmark_file):
    with patch("envswitch.bookmark.load_profiles", return_value=_PROFILES):
        add_bookmark("mybm", "dev", "a dev bookmark", path=bookmark_file)
    bms = load_bookmarks(bookmark_file)
    assert "mybm" in bms
    assert bms["mybm"]["profile"] == "dev"
    assert bms["mybm"]["description"] == "a dev bookmark"


def test_add_bookmark_profile_not_found(bookmark_file):
    with patch("envswitch.bookmark.load_profiles", return_value=_PROFILES):
        with pytest.raises(BookmarkError, match="does not exist"):
            add_bookmark("mybm", "staging", path=bookmark_file)


def test_add_bookmark_duplicate_raises(bookmark_file):
    with patch("envswitch.bookmark.load_profiles", return_value=_PROFILES):
        add_bookmark("mybm", "dev", path=bookmark_file)
        with pytest.raises(BookmarkError, match="already exists"):
            add_bookmark("mybm", "prod", path=bookmark_file)


def test_remove_bookmark_success(bookmark_file):
    save_bookmarks({"mybm": {"profile": "dev", "description": ""}}, bookmark_file)
    remove_bookmark("mybm", path=bookmark_file)
    assert load_bookmarks(bookmark_file) == {}


def test_remove_bookmark_not_found(bookmark_file):
    with pytest.raises(BookmarkError, match="not found"):
        remove_bookmark("ghost", path=bookmark_file)


def test_get_bookmark_success(bookmark_file):
    save_bookmarks({"bm": {"profile": "prod", "description": ""}}, bookmark_file)
    result = get_bookmark("bm", path=bookmark_file)
    assert result["profile"] == "prod"


def test_get_bookmark_not_found(bookmark_file):
    with pytest.raises(BookmarkError, match="not found"):
        get_bookmark("nope", path=bookmark_file)


def test_list_bookmarks_empty(bookmark_file):
    assert list_bookmarks(bookmark_file) == []


def test_list_bookmarks_returns_all(bookmark_file):
    save_bookmarks(
        {
            "a": {"profile": "dev", "description": "first"},
            "b": {"profile": "prod", "description": ""},
        },
        bookmark_file,
    )
    items = list_bookmarks(bookmark_file)
    names = [i["name"] for i in items]
    assert "a" in names and "b" in names
