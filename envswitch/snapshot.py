"""Snapshot: save and restore profile snapshots."""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any

from envswitch.storage import load_profiles, get_profile


def get_snapshots_path() -> Path:
    base = Path.home() / ".config" / "envswitch"
    base.mkdir(parents=True, exist_ok=True)
    return base / "snapshots.json"


def load_snapshots(path: Path | None = None) -> dict[str, Any]:
    p = path or get_snapshots_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def save_snapshots(snapshots: dict[str, Any], path: Path | None = None) -> None:
    p = path or get_snapshots_path()
    p.write_text(json.dumps(snapshots, indent=2))


def create_snapshot(profile_name: str, label: str | None = None, path: Path | None = None) -> str:
    """Snapshot current vars of a profile. Returns snapshot id."""
    vars_ = get_profile(profile_name)
    if vars_ is None:
        raise KeyError(f"Profile '{profile_name}' not found.")
    snapshots = load_snapshots(path)
    ts = int(time.time())
    snap_id = f"{profile_name}:{ts}"
    snapshots[snap_id] = {
        "profile": profile_name,
        "label": label or "",
        "timestamp": ts,
        "vars": vars_,
    }
    save_snapshots(snapshots, path)
    return snap_id


def list_snapshots(profile_name: str | None = None, path: Path | None = None) -> list[dict]:
    snapshots = load_snapshots(path)
    result = [
        {"id": k, **v}
        for k, v in snapshots.items()
        if profile_name is None or v.get("profile") == profile_name
    ]
    return sorted(result, key=lambda x: x["timestamp"])


def restore_snapshot(snap_id: str, path: Path | None = None) -> dict[str, str]:
    """Return vars from snapshot (caller is responsible for saving to profile)."""
    snapshots = load_snapshots(path)
    if snap_id not in snapshots:
        raise KeyError(f"Snapshot '{snap_id}' not found.")
    return dict(snapshots[snap_id]["vars"])


def delete_snapshot(snap_id: str, path: Path | None = None) -> None:
    snapshots = load_snapshots(path)
    if snap_id not in snapshots:
        raise KeyError(f"Snapshot '{snap_id}' not found.")
    del snapshots[snap_id]
    save_snapshots(snapshots, path)
