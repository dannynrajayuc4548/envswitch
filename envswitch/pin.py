"""Pin a profile as the default for a directory."""

import json
from pathlib import Path
from typing import Optional

PIN_FILE = ".envswitch_pin"


class PinNotFoundError(Exception):
    pass


def get_pin_path(directory: Optional[str] = None) -> Path:
    base = Path(directory) if directory else Path.cwd()
    return base / PIN_FILE


def read_pin(directory: Optional[str] = None) -> Optional[str]:
    path = get_pin_path(directory)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if isinstance(data, dict) and "profile" in data:
            return data["profile"]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def write_pin(profile_name: str, directory: Optional[str] = None) -> Path:
    path = get_pin_path(directory)
    path.write_text(json.dumps({"profile": profile_name}, indent=2))
    return path


def remove_pin(directory: Optional[str] = None) -> None:
    path = get_pin_path(directory)
    if not path.exists():
        raise PinNotFoundError(f"No pin file found at {path}")
    path.unlink()


def resolve_pin(directory: Optional[str] = None) -> str:
    profile = read_pin(directory)
    if profile is None:
        raise PinNotFoundError("No pinned profile found in this directory")
    return profile
