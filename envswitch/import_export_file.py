"""Import and export profiles to/from JSON or TOML files."""
import json
from pathlib import Path
from typing import Optional

from envswitch.storage import load_profiles, save_profiles


class ImportError(Exception):
    pass


class ExportFileError(Exception):
    pass


def export_to_file(path: str, profile_names: Optional[list] = None) -> dict:
    """Export profiles to a JSON file. Returns exported profiles dict."""
    profiles = load_profiles()
    if profile_names:
        missing = [n for n in profile_names if n not in profiles]
        if missing:
            raise ExportFileError(f"Profiles not found: {', '.join(missing)}")
        data = {n: profiles[n] for n in profile_names}
    else:
        data = dict(profiles)
    out = {"envswitch_profiles": data}
    Path(path).write_text(json.dumps(out, indent=2))
    return data


def import_from_file(path: str, overwrite: bool = False) -> list:
    """Import profiles from a JSON file. Returns list of imported profile names."""
    try:
        raw = Path(path).read_text()
    except FileNotFoundError:
        raise ImportError(f"File not found: {path}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ImportError(f"Invalid JSON: {e}")
    if not isinstance(data, dict) or "envswitch_profiles" not in data:
        raise ImportError("Missing 'envswitch_profiles' key in file")
    incoming = data["envswitch_profiles"]
    if not isinstance(incoming, dict):
        raise ImportError("'envswitch_profiles' must be a dict")
    profiles = load_profiles()
    imported = []
    for name, vars_ in incoming.items():
        if not isinstance(vars_, dict):
            raise ImportError(f"Profile '{name}' vars must be a dict")
        if name in profiles and not overwrite:
            continue
        profiles[name] = vars_
        imported.append(name)
    save_profiles(profiles)
    return imported
