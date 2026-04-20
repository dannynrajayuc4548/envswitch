"""Tests for envswitch.promote and envswitch.cli_promote."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from envswitch.promote import promote_profile, ProfileNotFoundError, PromoteError
from envswitch.cli_promote import promote_cmd


SAMPLE = {
    "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
    "staging": {"DB_HOST": "staging.db", "API_KEY": "abc123"},
    "prod": {"DB_HOST": "prod.db"},
}


def _patched(profiles):
    """Return context managers that mock load/save with a copy of *profiles*."""
    store = {k: dict(v) for k, v in profiles.items()}

    def fake_load():
        return {k: dict(v) for k, v in store.items()}

    def fake_save(data):
        store.clear()
        store.update({k: dict(v) for k, v in data.items()})

    return patch("envswitch.promote.load_profiles", fake_load), patch(
        "envswitch.promote.save_profiles", fake_save
    )


def test_promote_all_vars_no_conflict():
    p1, p2 = _patched({"src": {"FOO": "1", "BAR": "2"}, "dst": {"BAZ": "3"}})
    with p1, p2:
        result = promote_profile("src", "dst")
    assert result == {"BAZ": "3", "FOO": "1", "BAR": "2"}


def test_promote_specific_keys():
    p1, p2 = _patched({"src": {"FOO": "1", "BAR": "2"}, "dst": {}})
    with p1, p2:
        result = promote_profile("src", "dst", keys=["FOO"])
    assert result == {"FOO": "1"}
    assert "BAR" not in result


def test_promote_conflict_raises_without_overwrite():
    p1, p2 = _patched({"src": {"FOO": "new"}, "dst": {"FOO": "old"}})
    with p1, p2:
        with pytest.raises(PromoteError, match="FOO"):
            promote_profile("src", "dst", overwrite=False)


def test_promote_conflict_resolved_with_overwrite():
    p1, p2 = _patched({"src": {"FOO": "new"}, "dst": {"FOO": "old"}})
    with p1, p2:
        result = promote_profile("src", "dst", overwrite=True)
    assert result["FOO"] == "new"


def test_promote_source_not_found():
    p1, p2 = _patched({"dst": {}})
    with p1, p2:
        with pytest.raises(ProfileNotFoundError, match="src"):
            promote_profile("src", "dst")


def test_promote_destination_not_found():
    p1, p2 = _patched({"src": {"A": "1"}})
    with p1, p2:
        with pytest.raises(ProfileNotFoundError, match="dst"):
            promote_profile("src", "dst")


def test_promote_missing_specific_key_raises():
    p1, p2 = _patched({"src": {"FOO": "1"}, "dst": {}})
    with p1, p2:
        with pytest.raises(PromoteError, match="MISSING"):
            promote_profile("src", "dst", keys=["MISSING"])


# --- CLI tests ---


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_promote_success(runner):
    p1, p2 = _patched({"dev": {"FOO": "1"}, "staging": {"BAR": "2"}})
    with p1, p2:
        result = runner.invoke(promote_cmd, ["run", "dev", "staging"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "staging" in result.output


def test_cli_promote_conflict_error(runner):
    p1, p2 = _patched({"dev": {"FOO": "1"}, "staging": {"FOO": "2"}})
    with p1, p2:
        result = runner.invoke(promote_cmd, ["run", "dev", "staging"])
    assert result.exit_code != 0
    assert "FOO" in result.output


def test_cli_promote_with_key(runner):
    p1, p2 = _patched({"dev": {"FOO": "1", "BAR": "2"}, "staging": {}})
    with p1, p2:
        result = runner.invoke(promote_cmd, ["run", "dev", "staging", "--key", "FOO"])
    assert result.exit_code == 0
