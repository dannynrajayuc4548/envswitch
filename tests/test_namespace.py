"""Tests for envswitch.namespace and envswitch.cli_namespace."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envswitch.cli_namespace import namespace_cmd
from envswitch.namespace import (
    NamespaceError,
    add_to_namespace,
    find_profile_namespaces,
    get_namespace_members,
    list_namespaces,
    load_namespaces,
    remove_from_namespace,
    save_namespaces,
)


SAMPLE_PROFILES = {
    "dev": {"DB_HOST": "localhost"},
    "prod": {"DB_HOST": "prod.example.com"},
    "staging": {"DB_HOST": "staging.example.com"},
}


@pytest.fixture()
def mock_storage(tmp_path, monkeypatch):
    ns_file = tmp_path / "namespaces.json"
    monkeypatch.setattr("envswitch.namespace.get_namespaces_path", lambda: ns_file)
    monkeypatch.setattr("envswitch.namespace.load_profiles", lambda: SAMPLE_PROFILES)
    return ns_file


def test_load_namespaces_missing_file(mock_storage):
    assert load_namespaces() == {}


def test_load_namespaces_invalid_json(mock_storage):
    mock_storage.write_text("not json")
    assert load_namespaces() == {}


def test_save_and_load_namespaces(mock_storage):
    data = {"backend": ["dev", "prod"]}
    save_namespaces(data)
    assert load_namespaces() == data


def test_add_to_namespace_success(mock_storage):
    add_to_namespace("backend", "dev")
    assert "dev" in load_namespaces()["backend"]


def test_add_to_namespace_profile_not_found(mock_storage):
    with pytest.raises(NamespaceError, match="not found"):
        add_to_namespace("backend", "ghost")


def test_add_to_namespace_no_duplicates(mock_storage):
    add_to_namespace("backend", "dev")
    add_to_namespace("backend", "dev")
    assert load_namespaces()["backend"].count("dev") == 1


def test_remove_from_namespace_success(mock_storage):
    save_namespaces({"backend": ["dev", "prod"]})
    remove_from_namespace("backend", "dev")
    assert "dev" not in load_namespaces().get("backend", [])


def test_remove_last_member_deletes_namespace(mock_storage):
    save_namespaces({"solo": ["dev"]})
    remove_from_namespace("solo", "dev")
    assert "solo" not in load_namespaces()


def test_remove_from_missing_namespace(mock_storage):
    with pytest.raises(NamespaceError, match="not found"):
        remove_from_namespace("ghost", "dev")


def test_list_namespaces(mock_storage):
    save_namespaces({"z_ns": ["dev"], "a_ns": ["prod"]})
    assert list_namespaces() == ["a_ns", "z_ns"]


def test_get_namespace_members(mock_storage):
    save_namespaces({"backend": ["dev", "prod"]})
    assert get_namespace_members("backend") == ["dev", "prod"]


def test_get_namespace_members_not_found(mock_storage):
    with pytest.raises(NamespaceError):
        get_namespace_members("ghost")


def test_find_profile_namespaces(mock_storage):
    save_namespaces({"backend": ["dev", "prod"], "all": ["dev", "staging"]})
    result = find_profile_namespaces("dev")
    assert result == ["all", "backend"]


# --- CLI tests ---


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def patched(tmp_path, monkeypatch):
    ns_file = tmp_path / "namespaces.json"
    monkeypatch.setattr("envswitch.namespace.get_namespaces_path", lambda: ns_file)
    monkeypatch.setattr("envswitch.namespace.load_profiles", lambda: SAMPLE_PROFILES)
    return ns_file


def test_cli_ns_add_success(runner, patched):
    result = runner.invoke(namespace_cmd, ["add", "backend", "dev"])
    assert result.exit_code == 0
    assert "Added 'dev'" in result.output


def test_cli_ns_add_profile_not_found(runner, patched):
    result = runner.invoke(namespace_cmd, ["add", "backend", "ghost"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_cli_ns_remove_success(runner, patched):
    patched.write_text(json.dumps({"backend": ["dev"]}))
    result = runner.invoke(namespace_cmd, ["remove", "backend", "dev"])
    assert result.exit_code == 0
    assert "Removed 'dev'" in result.output


def test_cli_ns_list(runner, patched):
    patched.write_text(json.dumps({"backend": ["dev"], "frontend": ["prod"]}))
    result = runner.invoke(namespace_cmd, ["list"])
    assert "backend" in result.output
    assert "frontend" in result.output


def test_cli_ns_list_empty(runner, patched):
    result = runner.invoke(namespace_cmd, ["list"])
    assert "No namespaces" in result.output


def test_cli_ns_show(runner, patched):
    patched.write_text(json.dumps({"backend": ["dev", "prod"]}))
    result = runner.invoke(namespace_cmd, ["show", "backend"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_cli_ns_find(runner, patched):
    patched.write_text(json.dumps({"backend": ["dev"], "all": ["dev", "prod"]}))
    result = runner.invoke(namespace_cmd, ["find", "dev"])
    assert "backend" in result.output
    assert "all" in result.output
