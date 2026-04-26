"""Tests for envswitch.cli_pipeline."""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from envswitch.cli_pipeline import pipeline_cmd

SAMPLE = {
    "base": {"HOST": "localhost", "PORT": "5432"},
    "prod": {"HOST": "prod.example.com", "DEBUG": "false"},
}


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_load(monkeypatch):
    monkeypatch.setattr("envswitch.pipeline.load_profiles", lambda: dict(SAMPLE))


def test_pipeline_run_dotenv_default(runner):
    result = runner.invoke(pipeline_cmd, ["run", "base"])
    assert result.exit_code == 0
    assert "HOST=localhost" in result.output
    assert "PORT=5432" in result.output


def test_pipeline_run_json_format(runner):
    result = runner.invoke(pipeline_cmd, ["run", "--format", "json", "base", "prod"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["HOST"] == "prod.example.com"
    assert data["PORT"] == "5432"


def test_pipeline_run_merge_order(runner):
    result = runner.invoke(pipeline_cmd, ["run", "base", "prod"])
    assert result.exit_code == 0
    assert "HOST=prod.example.com" in result.output


def test_pipeline_run_missing_profile(runner):
    result = runner.invoke(pipeline_cmd, ["run", "base", "missing"])
    assert result.exit_code != 0
    assert "missing" in result.output.lower() or "Error" in result.output


def test_pipeline_describe_shows_added(runner):
    result = runner.invoke(pipeline_cmd, ["describe", "base"])
    assert result.exit_code == 0
    assert "[base]" in result.output
    assert "HOST" in result.output


def test_pipeline_describe_shows_overridden(runner):
    result = runner.invoke(pipeline_cmd, ["describe", "base", "prod"])
    assert result.exit_code == 0
    assert "~" in result.output
    assert "localhost" in result.output


def test_pipeline_describe_missing_profile(runner):
    result = runner.invoke(pipeline_cmd, ["describe", "ghost"])
    assert result.exit_code != 0
