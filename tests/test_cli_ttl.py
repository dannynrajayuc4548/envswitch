"""CLI tests for the ttl command group."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envswitch.cli_ttl import ttl_cmd
from envswitch.ttl import save_ttl


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def ttl_file(tmp_path, monkeypatch):
    ttl_path = tmp_path / "ttl.json"
    monkeypatch.setattr("envswitch.ttl.get_ttl_path", lambda: ttl_path)
    return ttl_path


@pytest.fixture()
def sample_profiles():
    return {"dev": {"KEY": "val"}, "prod": {"KEY": "val"}}


def test_ttl_set_success(runner, sample_profiles):
    with patch("envswitch.cli_ttl.load_profiles", return_value=sample_profiles):
        result = runner.invoke(ttl_cmd, ["set", "dev", "300"])
    assert result.exit_code == 0
    assert "TTL set for 'dev'" in result.output


def test_ttl_set_profile_not_found(runner):
    with patch("envswitch.cli_ttl.load_profiles", return_value={}):
        result = runner.invoke(ttl_cmd, ["set", "ghost", "60"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_ttl_set_negative_seconds(runner, sample_profiles):
    with patch("envswitch.cli_ttl.load_profiles", return_value=sample_profiles):
        result = runner.invoke(ttl_cmd, ["set", "dev", "-5"])
    assert result.exit_code != 0


def test_ttl_remove_success(runner):
    save_ttl({"dev": time.time() + 300})
    result = runner.invoke(ttl_cmd, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_ttl_show_no_ttl(runner):
    result = runner.invoke(ttl_cmd, ["show", "dev"])
    assert result.exit_code == 0
    assert "No TTL" in result.output


def test_ttl_show_active(runner):
    save_ttl({"dev": time.time() + 9999})
    result = runner.invoke(ttl_cmd, ["show", "dev"])
    assert result.exit_code == 0
    assert "active" in result.output


def test_ttl_show_expired(runner):
    save_ttl({"dev": time.time() - 1})
    result = runner.invoke(ttl_cmd, ["show", "dev"])
    assert result.exit_code == 0
    assert "EXPIRED" in result.output


def test_ttl_list_empty(runner):
    result = runner.invoke(ttl_cmd, ["list"])
    assert result.exit_code == 0
    assert "No TTLs" in result.output


def test_ttl_list_entries(runner):
    save_ttl({"dev": time.time() + 100, "prod": time.time() - 1})
    result = runner.invoke(ttl_cmd, ["list"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output
    assert "EXPIRED" in result.output
