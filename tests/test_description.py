"""Tests for envswitch.description and envswitch.cli_description."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envswitch.cli_description import description_cmd
from envswitch.description import (
    get_description,
    list_descriptions,
    load_descriptions,
    remove_description,
    save_descriptions,
    set_description,
)


@pytest.fixture()
def descriptions_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    desc_path = tmp_path / "descriptions.json"
    monkeypatch.setattr("envswitch.description.get_descriptions_path", lambda: desc_path)
    return desc_path


@pytest.fixture()
def sample_profiles():
    return {"dev": {"API_KEY": "abc"}, "prod": {"API_KEY": "xyz"}}


def test_load_descriptions_missing_file(descriptions_file):
    assert load_descriptions() == {}


def test_load_descriptions_invalid_json(descriptions_file):
    descriptions_file.write_text("not json")
    assert load_descriptions() == {}


def test_load_descriptions_invalid_format(descriptions_file):
    descriptions_file.write_text(json.dumps(["a", "b"]))
    assert load_descriptions() == {}


def test_save_and_load_descriptions(descriptions_file):
    save_descriptions({"dev": "Development environment"})
    result = load_descriptions()
    assert result == {"dev": "Development environment"}


def test_set_description_success(descriptions_file, sample_profiles):
    with patch("envswitch.description.load_profiles", return_value=sample_profiles):
        set_description("dev", "My dev profile")
    assert load_descriptions()["dev"] == "My dev profile"


def test_set_description_profile_not_found(descriptions_file, sample_profiles):
    with patch("envswitch.description.load_profiles", return_value=sample_profiles):
        with pytest.raises(KeyError, match="not found"):
            set_description("staging", "Staging env")


def test_get_description_existing(descriptions_file):
    save_descriptions({"dev": "Dev env"})
    assert get_description("dev") == "Dev env"


def test_get_description_missing(descriptions_file):
    assert get_description("nonexistent") is None


def test_remove_description_success(descriptions_file):
    save_descriptions({"dev": "Dev env"})
    assert remove_description("dev") is True
    assert get_description("dev") is None


def test_remove_description_not_found(descriptions_file):
    assert remove_description("ghost") is False


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_desc_set_success(runner, descriptions_file, sample_profiles):
    with patch("envswitch.description.load_profiles", return_value=sample_profiles):
        result = runner.invoke(description_cmd, ["set", "dev", "Dev profile"])
    assert result.exit_code == 0
    assert "Description set for 'dev'" in result.output


def test_cli_desc_set_profile_not_found(runner, descriptions_file, sample_profiles):
    with patch("envswitch.description.load_profiles", return_value=sample_profiles):
        result = runner.invoke(description_cmd, ["set", "staging", "Staging"])
    assert result.exit_code == 1


def test_cli_desc_show_existing(runner, descriptions_file):
    save_descriptions({"dev": "Dev profile"})
    result = runner.invoke(description_cmd, ["show", "dev"])
    assert "Dev profile" in result.output


def test_cli_desc_show_missing(runner, descriptions_file):
    result = runner.invoke(description_cmd, ["show", "ghost"])
    assert "No description" in result.output


def test_cli_desc_remove_success(runner, descriptions_file):
    save_descriptions({"dev": "Dev profile"})
    result = runner.invoke(description_cmd, ["remove", "dev"])
    assert "removed" in result.output


def test_cli_desc_list(runner, descriptions_file):
    save_descriptions({"dev": "Dev", "prod": "Prod"})
    result = runner.invoke(description_cmd, ["list"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_cli_desc_list_empty(runner, descriptions_file):
    result = runner.invoke(description_cmd, ["list"])
    assert "No descriptions" in result.output
