"""Storage module for managing environment profiles on disk."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "envswitch"
DEFAULT_PROFILES_FILE = DEFAULT_CONFIG_DIR / "profiles.json"


def get_profiles_path() -> Path:
    """Return the path to the profiles file, respecting ENVSWITCH_CONFIG env var."""
    config_dir = os.environ.get("ENVSWITCH_CONFIG", str(DEFAULT_CONFIG_DIR))
    return Path(config_dir) / "profiles.json"


def load_profiles(path: Optional[Path] = None) -> Dict[str, Dict[str, str]]:
    """Load all profiles from disk. Returns empty dict if file does not exist."""
    profiles_path = path or get_profiles_path()
    if not profiles_path.exists():
        return {}
    with profiles_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid profiles file format at {profiles_path}")
    return data


def save_profiles(profiles: Dict[str, Dict[str, str]], path: Optional[Path] = None) -> None:
    """Persist all profiles to disk, creating directories as needed."""
    profiles_path = path or get_profiles_path()
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    with profiles_path.open("w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)
        f.write("\n")


def get_profile(name: str, path: Optional[Path] = None) -> Optional[Dict[str, str]]:
    """Retrieve a single profile by name. Returns None if not found."""
    profiles = load_profiles(path)
    return profiles.get(name)


def set_profile(name: str, variables: Dict[str, str], path: Optional[Path] = None) -> None:
    """Create or overwrite a profile with the given environment variables."""
    profiles = load_profiles(path)
    profiles[name] = variables
    save_profiles(profiles, path)


def delete_profile(name: str, path: Optional[Path] = None) -> bool:
    """Delete a profile by name. Returns True if deleted, False if not found."""
    profiles = load_profiles(path)
    if name not in profiles:
        return False
    del profiles[name]
    save_profiles(profiles, path)
    return True


def list_profile_names(path: Optional[Path] = None) -> list:
    """Return a sorted list of all profile names."""
    return sorted(load_profiles(path).keys())
