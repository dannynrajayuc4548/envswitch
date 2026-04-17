import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from envswitch.snapshot import (
    create_snapshot, list_snapshots, restore_snapshot, delete_snapshot, load_snapshots
)
from envswitch.cli_snapshot import snapshot_cmd


SAMPLE_PROFILES = {
    "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
    "prod": {"DB_HOST": "prod.db", "DEBUG": "false"},
}


@pytest.fixture
def snap_file(tmp_path):
    return tmp_path / "snapshots.json"


def test_create_snapshot_success(snap_file):
    with patch("envswitch.snapshot.get_profile", return_value={"K": "V"}):
        snap_id = create_snapshot("dev", path=snap_file)
    assert snap_id.startswith("dev:")
    data = load_snapshots(snap_file)
    assert snap_id in data
    assert data[snap_id]["vars"] == {"K": "V"}


def test_create_snapshot_profile_not_found(snap_file):
    with patch("envswitch.snapshot.get_profile", return_value=None):
        with pytest.raises(KeyError, match="not found"):
            create_snapshot("missing", path=snap_file)


def test_create_snapshot_with_label(snap_file):
    with patch("envswitch.snapshot.get_profile", return_value={"A": "1"}):
        snap_id = create_snapshot("dev", label="before-deploy", path=snap_file)
    data = load_snapshots(snap_file)
    assert data[snap_id]["label"] == "before-deploy"


def test_list_snapshots_all(snap_file):
    with patch("envswitch.snapshot.get_profile", return_value={"X": "1"}):
        create_snapshot("dev", path=snap_file)
        create_snapshot("prod", path=snap_file)
    snaps = list_snapshots(path=snap_file)
    assert len(snaps) == 2


def test_list_snapshots_filtered(snap_file):
    with patch("envswitch.snapshot.get_profile", return_value={"X": "1"}):
        create_snapshot("dev", path=snap_file)
        create_snapshot("prod", path=snap_file)
    snaps = list_snapshots("dev", path=snap_file)
    assert all(s["profile"] == "dev" for s in snaps)


def test_restore_snapshot(snap_file):
    with patch("envswitch.snapshot.get_profile", return_value={"K": "V"}):
        snap_id = create_snapshot("dev", path=snap_file)
    vars_ = restore_snapshot(snap_id, path=snap_file)
    assert vars_ == {"K": "V"}


def test_restore_snapshot_not_found(snap_file):
    with pytest.raises(KeyError, match="not found"):
        restore_snapshot("dev:9999", path=snap_file)


def test_delete_snapshot(snap_file):
    with patch("envswitch.snapshot.get_profile", return_value={"K": "V"}):
        snap_id = create_snapshot("dev", path=snap_file)
    delete_snapshot(snap_id, path=snap_file)
    assert snap_id not in load_snapshots(snap_file)


def test_cli_create_and_list(snap_file):
    runner = CliRunner()
    with patch("envswitch.snapshot.get_profile", return_value={"A": "1"}):
        with patch("envswitch.snapshot.get_snapshots_path", return_value=snap_file):
            result = runner.invoke(snapshot_cmd, ["create", "dev", "--label", "test"])
    assert result.exit_code == 0
    assert "Snapshot created" in result.output


def test_cli_restore_not_found():
    runner = CliRunner()
    with patch("envswitch.snapshot.get_snapshots_path", return_value=Path("/nonexistent/x.json")):
        result = runner.invoke(snapshot_cmd, ["restore", "dev:0000"])
    assert result.exit_code == 1
