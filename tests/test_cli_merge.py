"""Tests for the merge CLI command."""

import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from envswitch.cli_merge import merge_cmd


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def sample_profiles(tmp_path: Path) -> Path:
    path = tmp_path / "profiles.json"
    data = {
        "base": {"APP_ENV": "prod", "LOG_LEVEL": "info"},
        "overrides": {"APP_ENV": "staging", "DEBUG": "1"},
    }
    path.write_text(json.dumps(data))
    return path


def test_merge_success(runner: CliRunner, sample_profiles: Path) -> None:
    import envswitch.storage as storage
    storage._profiles_path = str(sample_profiles)  # type: ignore[attr-defined]
    result = runner.invoke(merge_cmd, ["base", "overrides", "-d", "combined"])
    assert result.exit_code == 0
    assert "combined" in result.output
    assert "2 profiles" in result.output


def test_merge_missing_source(runner: CliRunner, sample_profiles: Path) -> None:
    import envswitch.storage as storage
    storage._profiles_path = str(sample_profiles)  # type: ignore[attr-defined]
    result = runner.invoke(merge_cmd, ["base", "ghost", "-d", "out"])
    assert result.exit_code != 0
    assert "ghost" in result.output


def test_merge_destination_exists_no_overwrite(runner: CliRunner, sample_profiles: Path) -> None:
    import envswitch.storage as storage
    storage._profiles_path = str(sample_profiles)  # type: ignore[attr-defined]
    result = runner.invoke(merge_cmd, ["base", "overrides", "-d", "base"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_merge_destination_exists_with_overwrite(runner: CliRunner, sample_profiles: Path) -> None:
    import envswitch.storage as storage
    storage._profiles_path = str(sample_profiles)  # type: ignore[attr-defined]
    result = runner.invoke(merge_cmd, ["base", "overrides", "-d", "base", "--overwrite"])
    assert result.exit_code == 0


def test_merge_requires_two_sources(runner: CliRunner, sample_profiles: Path) -> None:
    import envswitch.storage as storage
    storage._profiles_path = str(sample_profiles)  # type: ignore[attr-defined]
    result = runner.invoke(merge_cmd, ["base", "-d", "out"])
    assert result.exit_code != 0
