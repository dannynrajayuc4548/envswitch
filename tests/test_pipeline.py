"""Tests for envswitch.pipeline."""

from __future__ import annotations

import pytest

from envswitch.pipeline import (
    PipelineError,
    ProfileNotFoundError,
    describe_pipeline,
    run_pipeline,
)

SAMPLE = {
    "base": {"HOST": "localhost", "PORT": "5432"},
    "prod": {"HOST": "prod.example.com", "DEBUG": "false"},
    "extra": {"EXTRA_VAR": "hello"},
}


@pytest.fixture(autouse=True)
def mock_load(monkeypatch):
    monkeypatch.setattr("envswitch.pipeline.load_profiles", lambda: dict(SAMPLE))


def test_run_pipeline_single_profile():
    result = run_pipeline(["base"])
    assert result == {"HOST": "localhost", "PORT": "5432"}


def test_run_pipeline_merges_left_to_right():
    result = run_pipeline(["base", "prod"])
    assert result["HOST"] == "prod.example.com"
    assert result["PORT"] == "5432"
    assert result["DEBUG"] == "false"


def test_run_pipeline_three_profiles():
    result = run_pipeline(["base", "prod", "extra"])
    assert result["EXTRA_VAR"] == "hello"
    assert result["HOST"] == "prod.example.com"


def test_run_pipeline_empty_raises():
    with pytest.raises(PipelineError, match="at least one"):
        run_pipeline([])


def test_run_pipeline_missing_profile_raises():
    with pytest.raises(ProfileNotFoundError, match="missing"):
        run_pipeline(["base", "missing"])


def test_describe_pipeline_added_vars():
    steps = describe_pipeline(["base", "prod"])
    base_step = steps[0]
    assert "HOST" in base_step["added"]
    assert base_step["overridden"] == {}


def test_describe_pipeline_overridden_vars():
    steps = describe_pipeline(["base", "prod"])
    prod_step = steps[1]
    assert "HOST" in prod_step["overridden"]
    old, new = prod_step["overridden"]["HOST"]
    assert old == "localhost"
    assert new == "prod.example.com"


def test_describe_pipeline_missing_profile_raises():
    with pytest.raises(ProfileNotFoundError):
        describe_pipeline(["base", "nope"])


def test_describe_pipeline_empty_raises():
    with pytest.raises(PipelineError):
        describe_pipeline([])
