"""Integration-style tests: pipeline CLI wired through a real profiles file."""

from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envswitch.cli_pipeline import pipeline_cmd
from envswitch.storage import save_profiles


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def profiles_file(tmp_path, monkeypatch):
    path = tmp_path / "profiles.json"
    monkeypatch.setattr("envswitch.storage.get_profiles_path", lambda: path)
    monkeypatch.setattr("envswitch.pipeline.load_profiles",
                        lambda: json.loads(path.read_text()) if path.exists() else {})
    return path


def test_run_pipeline_with_real_profiles(runner, profiles_file):
    save_profiles({
        "defaults": {"LOG_LEVEL": "info", "TIMEOUT": "30"},
        "overrides": {"LOG_LEVEL": "debug"},
    })
    result = runner.invoke(pipeline_cmd, ["run", "defaults", "overrides"])
    assert result.exit_code == 0
    assert "LOG_LEVEL=debug" in result.output
    assert "TIMEOUT=30" in result.output


def test_run_pipeline_json_with_real_profiles(runner, profiles_file):
    save_profiles({
        "a": {"X": "1"},
        "b": {"Y": "2"},
    })
    result = runner.invoke(pipeline_cmd, ["run", "--format", "json", "a", "b"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"X": "1", "Y": "2"}


def test_describe_pipeline_with_real_profiles(runner, profiles_file):
    save_profiles({
        "base": {"A": "1", "B": "2"},
        "patch": {"B": "99", "C": "3"},
    })
    result = runner.invoke(pipeline_cmd, ["describe", "base", "patch"])
    assert result.exit_code == 0
    assert "[base]" in result.output
    assert "[patch]" in result.output
    assert "B" in result.output
