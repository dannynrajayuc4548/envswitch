"""Tests for envswitch.reorder."""

import json
import pytest

from envswitch.reorder import reorder_profile, move_key, ProfileNotFoundError, ReorderError


@pytest.fixture
def profiles_file(tmp_path, monkeypatch):
    path = tmp_path / "profiles.json"
    data = {
        "dev": {"HOST": "localhost", "PORT": "8080", "DEBUG": "true"},
        "prod": {"HOST": "prod.example.com", "PORT": "443"},
    }
    path.write_text(json.dumps(data))
    monkeypatch.setattr("envswitch.storage.get_profiles_path", lambda: path)
    return path


def _read(path):
    return json.loads(path.read_text())


def test_reorder_profile_success(profiles_file):
    result = reorder_profile("dev", ["DEBUG", "HOST", "PORT"])
    assert list(result.keys()) == ["DEBUG", "HOST", "PORT"]


def test_reorder_profile_persists(profiles_file):
    reorder_profile("dev", ["PORT", "DEBUG", "HOST"])
    saved = _read(profiles_file)["dev"]
    assert list(saved.keys()) == ["PORT", "DEBUG", "HOST"]


def test_reorder_partial_order_appends_rest(profiles_file):
    result = reorder_profile("dev", ["PORT"], fill_missing=True)
    assert list(result.keys())[0] == "PORT"
    assert set(result.keys()) == {"HOST", "PORT", "DEBUG"}


def test_reorder_fill_missing_false_drops_unlisted(profiles_file):
    result = reorder_profile("dev", ["PORT", "HOST"], fill_missing=False)
    assert list(result.keys()) == ["PORT", "HOST"]
    assert "DEBUG" not in result


def test_reorder_profile_not_found(profiles_file):
    with pytest.raises(ProfileNotFoundError):
        reorder_profile("nonexistent", ["HOST"])


def test_reorder_unknown_key_raises(profiles_file):
    with pytest.raises(ReorderError, match="UNKNOWN"):
        reorder_profile("dev", ["HOST", "UNKNOWN"])


def test_move_key_to_front(profiles_file):
    result = move_key("dev", "DEBUG", 0)
    assert list(result.keys())[0] == "DEBUG"


def test_move_key_to_end(profiles_file):
    result = move_key("dev", "HOST", 10)  # beyond length clamps to end
    assert list(result.keys())[-1] == "HOST"


def test_move_key_to_middle(profiles_file):
    result = move_key("dev", "DEBUG", 1)
    keys = list(result.keys())
    assert keys[1] == "DEBUG"


def test_move_key_persists(profiles_file):
    move_key("dev", "PORT", 0)
    saved = _read(profiles_file)["dev"]
    assert list(saved.keys())[0] == "PORT"


def test_move_key_profile_not_found(profiles_file):
    with pytest.raises(ProfileNotFoundError):
        move_key("ghost", "HOST", 0)


def test_move_key_missing_key_raises(profiles_file):
    with pytest.raises(ReorderError, match="MISSING"):
        move_key("dev", "MISSING", 0)
