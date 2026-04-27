"""Hotkey bindings: associate keyboard shortcuts with profile names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envswitch.storage import get_profiles_path, load_profiles


class HotkeyError(Exception):
    pass


def get_hotkeys_path() -> Path:
    return get_profiles_path().parent / "hotkeys.json"


def load_hotkeys() -> Dict[str, str]:
    path = get_hotkeys_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}


def save_hotkeys(hotkeys: Dict[str, str]) -> None:
    path = get_hotkeys_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(hotkeys, indent=2))


def bind_hotkey(key: str, profile: str) -> None:
    """Bind *key* to *profile*, raising HotkeyError if the profile does not exist."""
    profiles = load_profiles()
    if profile not in profiles:
        raise HotkeyError(f"Profile '{profile}' not found.")
    hotkeys = load_hotkeys()
    hotkeys[key] = profile
    save_hotkeys(hotkeys)


def unbind_hotkey(key: str) -> None:
    """Remove the binding for *key*, raising HotkeyError if it is not bound."""
    hotkeys = load_hotkeys()
    if key not in hotkeys:
        raise HotkeyError(f"Hotkey '{key}' is not bound.")
    del hotkeys[key]
    save_hotkeys(hotkeys)


def resolve_hotkey(key: str) -> Optional[str]:
    """Return the profile name bound to *key*, or None if unbound."""
    return load_hotkeys().get(key)


def list_hotkeys() -> Dict[str, str]:
    """Return all hotkey → profile mappings."""
    return load_hotkeys()
