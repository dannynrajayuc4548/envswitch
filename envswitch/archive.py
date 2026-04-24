"""Archive and restore deleted profiles."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from envswitch.storage import get_profiles_path, load_profiles, save_profiles


class ArchiveError(Exception):
    pass


def get_archive_path() -> Path:
    return get_profiles_path().parent / "archive.json"


def load_archive() -> Dict[str, list]:
    path = get_archive_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def save_archive(data: Dict[str, list]) -> None:
    path = get_archive_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def archive_profile(name: str) -> None:
    """Move a profile from active profiles into the archive."""
    profiles = load_profiles()
    if name not in profiles:
        raise ArchiveError(f"Profile '{name}' not found.")
    archive = load_archive()
    entry = {
        "vars": profiles.pop(name),
        "archived_at": datetime.now(timezone.utc).isoformat(),
    }
    archive.setdefault(name, []).append(entry)
    save_profiles(profiles)
    save_archive(archive)


def list_archived(name: Optional[str] = None) -> Dict[str, list]:
    """Return archived entries, optionally filtered by profile name."""
    archive = load_archive()
    if name is not None:
        return {name: archive.get(name, [])}
    return archive


def restore_profile(name: str, index: int = -1, overwrite: bool = False) -> None:
    """Restore an archived profile back to active profiles."""
    archive = load_archive()
    if name not in archive or not archive[name]:
        raise ArchiveError(f"No archived versions of '{name}' found.")
    profiles = load_profiles()
    if name in profiles and not overwrite:
        raise ArchiveError(
            f"Profile '{name}' already exists. Use overwrite=True to replace it."
        )
    entries: List[dict] = archive[name]
    try:
        entry = entries[index]
    except IndexError:
        raise ArchiveError(f"Archive index {index} out of range for '{name}'.")
    profiles[name] = entry["vars"]
    save_profiles(profiles)
