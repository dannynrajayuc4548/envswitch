"""Profile priority management — assign numeric priority levels to profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from envswitch.storage import load_profiles


class PriorityError(Exception):
    pass


def get_priority_path() -> Path:
    from envswitch.storage import get_profiles_path
    return get_profiles_path().parent / "priorities.json"


def load_priorities() -> Dict[str, int]:
    path = get_priority_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(v, int)}


def save_priorities(priorities: Dict[str, int]) -> None:
    path = get_priority_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(priorities, indent=2))


def set_priority(profile_name: str, level: int) -> None:
    profiles = load_profiles()
    if profile_name not in profiles:
        raise PriorityError(f"Profile '{profile_name}' not found.")
    priorities = load_priorities()
    priorities[profile_name] = level
    save_priorities(priorities)


def remove_priority(profile_name: str) -> None:
    priorities = load_priorities()
    if profile_name not in priorities:
        raise PriorityError(f"No priority set for profile '{profile_name}'.")
    del priorities[profile_name]
    save_priorities(priorities)


def get_priority(profile_name: str) -> Optional[int]:
    return load_priorities().get(profile_name)


def list_by_priority() -> List[Tuple[str, int]]:
    """Return all profiles that have a priority, sorted highest first."""
    priorities = load_priorities()
    return sorted(priorities.items(), key=lambda x: x[1], reverse=True)
