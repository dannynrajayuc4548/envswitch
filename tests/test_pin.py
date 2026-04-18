"""Tests for envswitch.pin and envswitch.cli_pin."""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch

from envswitch.pin import write_pin, read_pin, remove_pin, resolve_pin, PinNotFoundError
from envswitch.cli_pin import pin_cmd


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


def test_write_and_read_pin(tmp_dir):
    write_pin("production", tmp_dir)
    assert read_pin(tmp_dir) == "production"


def test_read_pin_missing_file(tmp_dir):
    assert read_pin(tmp_dir) is None


def test_read_pin_invalid_json(tmp_dir):
    pin_path = Path(tmp_dir) / ".envswitch_pin"
    pin_path.write_text("not json")
    assert read_pin(tmp_dir) is None


def test_remove_pin(tmp_dir):
    write_pin("staging", tmp_dir)
    remove_pin(tmp_dir)
    assert read_pin(tmp_dir) is None


def test_remove_pin_not_found(tmp_dir):
    with pytest.raises(PinNotFoundError):
        remove_pin(tmp_dir)


def test_resolve_pin(tmp_dir):
    write_pin("dev", tmp_dir)
    assert resolve_pin(tmp_dir) == "dev"


def test_resolve_pin_missing(tmp_dir):
    with pytest.raises(PinNotFoundError):
        resolve_pin(tmp_dir)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_profiles():
    return {"dev": {"KEY": "val"}, "prod": {"KEY": "prod_val"}}


def test_cli_pin_set(runner, sample_profiles, tmp_path):
    with patch("envswitch.cli_pin.load_profiles", return_value=sample_profiles):
        result = runner.invoke(pin_cmd, ["set", "dev", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "Pinned 'dev'" in result.output


def test_cli_pin_set_unknown_profile(runner, sample_profiles, tmp_path):
    with patch("envswitch.cli_pin.load_profiles", return_value=sample_profiles):
        result = runner.invoke(pin_cmd, ["set", "ghost", "--dir", str(tmp_path)])
    assert result.exit_code == 1


def test_cli_pin_show(runner, tmp_path):
    write_pin("prod", str(tmp_path))
    result = runner.invoke(pin_cmd, ["show", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_cli_pin_show_none(runner, tmp_path):
    result = runner.invoke(pin_cmd, ["show", "--dir", str(tmp_path)])
    assert "No profile pinned" in result.output


def test_cli_pin_remove(runner, tmp_path):
    write_pin("dev", str(tmp_path))
    result = runner.invoke(pin_cmd, ["remove", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "Pin removed" in result.output


def test_cli_pin_remove_not_found(runner, tmp_path):
    result = runner.invoke(pin_cmd, ["remove", "--dir", str(tmp_path)])
    assert result.exit_code == 1
