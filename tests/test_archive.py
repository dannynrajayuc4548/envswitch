"""Tests for envswitch.archive."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envswitch.archive import (
    ArchiveError,
    archive_profile,
    get_archive_path,
    list_archived,
    load_archive,
    restore_profile,
)


@pytest.fixture(autouse=True)
def patch_paths(tmp_path, monkeypatch):
    profiles_file = tmp_path / "profiles.json"
    archive_file = tmp_path / "archive.json"

    monkeypatch.setattr("envswitch.archive.get_profiles_path", lambda: profiles_file)
    monkeypatch.setattr("envswitch.archive.get_archive_path", lambda: archive_file)
    monkeypatch.setattr("envswitch.storage.get_profiles_path", lambda: profiles_file)

    profiles_file.write_text(json.dumps({"dev": {"FOO": "bar"}, "prod": {"FOO": "baz"}}))
    yield profiles_file, archive_file


def _read_profiles(profiles_file):
    return json.loads(profiles_file.read_text())


def test_archive_profile_removes_from_active(patch_paths):
    profiles_file, _ = patch_paths
    archive_profile("dev")
    profiles = _read_profiles(profiles_file)
    assert "dev" not in profiles
    assert "prod" in profiles


def test_archive_profile_stores_in_archive(patch_paths):
    _, archive_file = patch_paths
    archive_profile("dev")
    data = json.loads(archive_file.read_text())
    assert "dev" in data
    assert len(data["dev"]) == 1
    assert data["dev"][0]["vars"] == {"FOO": "bar"}
    assert "archived_at" in data["dev"][0]


def test_archive_profile_not_found_raises():
    with pytest.raises(ArchiveError, match="not found"):
        archive_profile("nonexistent")


def test_archive_same_profile_twice_appends(patch_paths):
    _, archive_file = patch_paths
    archive_profile("dev")
    # Put dev back so we can archive again
    profiles_file, _ = patch_paths
    profiles = _read_profiles(profiles_file)
    profiles["dev"] = {"FOO": "v2"}
    profiles_file.write_text(json.dumps(profiles))
    archive_profile("dev")
    data = json.loads(archive_file.read_text())
    assert len(data["dev"]) == 2


def test_list_archived_returns_all(patch_paths):
    archive_profile("dev")
    result = list_archived()
    assert "dev" in result


def test_list_archived_filtered_by_name(patch_paths):
    archive_profile("dev")
    result = list_archived("dev")
    assert "dev" in result
    assert "prod" not in result


def test_restore_profile_success(patch_paths):
    profiles_file, _ = patch_paths
    archive_profile("dev")
    restore_profile("dev")
    profiles = _read_profiles(profiles_file)
    assert "dev" in profiles
    assert profiles["dev"] == {"FOO": "bar"}


def test_restore_profile_not_archived_raises():
    with pytest.raises(ArchiveError, match="No archived versions"):
        restore_profile("ghost")


def test_restore_profile_exists_no_overwrite_raises(patch_paths):
    archive_profile("dev")
    # Put dev back manually
    profiles_file, _ = patch_paths
    profiles = _read_profiles(profiles_file)
    profiles["dev"] = {"FOO": "existing"}
    profiles_file.write_text(json.dumps(profiles))
    with pytest.raises(ArchiveError, match="already exists"):
        restore_profile("dev", overwrite=False)


def test_restore_profile_overwrite(patch_paths):
    profiles_file, _ = patch_paths
    archive_profile("dev")
    profiles = _read_profiles(profiles_file)
    profiles["dev"] = {"FOO": "existing"}
    profiles_file.write_text(json.dumps(profiles))
    restore_profile("dev", overwrite=True)
    profiles = _read_profiles(profiles_file)
    assert profiles["dev"] == {"FOO": "bar"}
