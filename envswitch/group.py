"""Profile grouping — assign profiles to named groups and query by group."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envswitch.storage import load_profiles


class GroupError(Exception):
    pass


def get_groups_path() -> Path:
    from envswitch.storage import get_profiles_path
    return get_profiles_path().parent / "groups.json"


def load_groups() -> Dict[str, List[str]]:
    path = get_groups_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(v, list)}


def save_groups(groups: Dict[str, List[str]]) -> None:
    get_groups_path().write_text(json.dumps(groups, indent=2))


def add_to_group(group: str, profile: str) -> None:
    profiles = load_profiles()
    if profile not in profiles:
        raise GroupError(f"Profile '{profile}' not found.")
    groups = load_groups()
    members = groups.setdefault(group, [])
    if profile not in members:
        members.append(profile)
    save_groups(groups)


def remove_from_group(group: str, profile: str) -> None:
    groups = load_groups()
    if group not in groups:
        raise GroupError(f"Group '{group}' not found.")
    if profile not in groups[group]:
        raise GroupError(f"Profile '{profile}' is not in group '{group}'.")
    groups[group].remove(profile)
    if not groups[group]:
        del groups[group]
    save_groups(groups)


def list_groups() -> Dict[str, List[str]]:
    return load_groups()


def get_group_members(group: str) -> List[str]:
    groups = load_groups()
    if group not in groups:
        raise GroupError(f"Group '{group}' not found.")
    return groups[group]


def delete_group(group: str) -> None:
    groups = load_groups()
    if group not in groups:
        raise GroupError(f"Group '{group}' not found.")
    del groups[group]
    save_groups(groups)
