"""Profile locking — prevent accidental modification of profiles."""

import json
from pathlib import Path
from envswitch.storage import get_profiles_path


def get_lock_path() -> Path:
    return get_profiles_path().parent / "locks.json"


def load_locks() -> list[str]:
    path = get_lock_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_locks(locks: list[str]) -> None:
    path = get_lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(locks, indent=2))


def lock_profile(name: str) -> None:
    locks = load_locks()
    if name not in locks:
        locks.append(name)
        save_locks(locks)


def unlock_profile(name: str) -> None:
    locks = load_locks()
    if name in locks:
        locks.remove(name)
        save_locks(locks)


def is_locked(name: str) -> bool:
    return name in load_locks()


def get_locked_profiles() -> list[str]:
    return load_locks()


class ProfileLockedError(Exception):
    """Raised when attempting to modify a locked profile."""
