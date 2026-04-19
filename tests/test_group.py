import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envswitch.group import (
    GroupError, add_to_group, remove_from_group,
    list_groups, get_group_members, delete_group, load_groups, save_groups,
)

SAMPLE_PROFILES = {
    "dev": {"DB": "dev-db"},
    "prod": {"DB": "prod-db"},
    "staging": {"DB": "staging-db"},
}


@pytest.fixture
def groups_file(tmp_path, monkeypatch):
    gfile = tmp_path / "groups.json"
    monkeypatch.setattr("envswitch.group.get_groups_path", lambda: gfile)
    monkeypatch.setattr("envswitch.group.load_profiles", lambda: SAMPLE_PROFILES)
    return gfile


def test_load_groups_missing_file(groups_file):
    assert load_groups() == {}


def test_load_groups_invalid_json(groups_file):
    groups_file.write_text("not json")
    assert load_groups() == {}


def test_add_to_group_success(groups_file):
    add_to_group("backend", "dev")
    data = json.loads(groups_file.read_text())
    assert "dev" in data["backend"]


def test_add_to_group_profile_not_found(groups_file):
    with pytest.raises(GroupError, match="not found"):
        add_to_group("backend", "ghost")


def test_add_to_group_no_duplicate(groups_file):
    add_to_group("backend", "dev")
    add_to_group("backend", "dev")
    data = json.loads(groups_file.read_text())
    assert data["backend"].count("dev") == 1


def test_remove_from_group_success(groups_file):
    add_to_group("backend", "dev")
    add_to_group("backend", "prod")
    remove_from_group("backend", "dev")
    assert "dev" not in get_group_members("backend")


def test_remove_last_member_deletes_group(groups_file):
    add_to_group("solo", "dev")
    remove_from_group("solo", "dev")
    assert "solo" not in list_groups()


def test_remove_from_missing_group(groups_file):
    with pytest.raises(GroupError, match="not found"):
        remove_from_group("nope", "dev")


def test_get_group_members(groups_file):
    add_to_group("g", "dev")
    add_to_group("g", "prod")
    members = get_group_members("g")
    assert set(members) == {"dev", "prod"}


def test_get_group_members_not_found(groups_file):
    with pytest.raises(GroupError):
        get_group_members("missing")


def test_delete_group(groups_file):
    add_to_group("tmp", "dev")
    delete_group("tmp")
    assert "tmp" not in list_groups()


def test_delete_group_not_found(groups_file):
    with pytest.raises(GroupError):
        delete_group("ghost")
