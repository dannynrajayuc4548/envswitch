"""Audit log for profile changes (set, delete, copy, rename, merge)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

from envswitch.storage import get_profiles_path


def get_audit_path() -> Path:
    return get_profiles_path().parent / "audit.json"


def load_audit() -> List[Dict[str, Any]]:
    path = get_audit_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        return []


def save_audit(entries: List[Dict[str, Any]]) -> None:
    path = get_audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2))


def record_event(action: str, profile: str, details: Dict[str, Any] | None = None) -> None:
    entries = load_audit()
    entry: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
    }
    if details:
        entry["details"] = details
    entries.append(entry)
    save_audit(entries)


def get_audit(profile: str | None = None, limit: int = 50) -> List[Dict[str, Any]]:
    entries = load_audit()
    if profile:
        entries = [e for e in entries if e.get("profile") == profile]
    return entries[-limit:]


def clear_audit() -> None:
    save_audit([])
