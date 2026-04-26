"""Profile description/metadata management for envswitch."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

APP_DIR = Path.home() / ".envswitch"


def get_descriptions_path() -> Path:
    return APP_DIR / "descriptions.json"


def load_descriptions() -> dict[str, str]:
    path = get_descriptions_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}


def save_descriptions(descriptions: dict[str, str]) -> None:
    path = get_descriptions_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(descriptions, indent=2))


def set_description(profile_name: str, description: str) -> None:
    from envswitch.storage import load_profiles
    profiles = load_profiles()
    if profile_name not in profiles:
        raise KeyError(f"Profile '{profile_name}' not found.")
    descs = load_descriptions()
    descs[profile_name] = description
    save_descriptions(descs)


def get_description(profile_name: str) -> Optional[str]:
    descs = load_descriptions()
    return descs.get(profile_name)


def remove_description(profile_name: str) -> bool:
    descs = load_descriptions()
    if profile_name not in descs:
        return False
    del descs[profile_name]
    save_descriptions(descs)
    return True


def list_descriptions() -> dict[str, str]:
    return load_descriptions()
