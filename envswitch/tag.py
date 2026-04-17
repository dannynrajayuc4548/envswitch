"""Tag profiles with labels for grouping and filtering."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from envswitch.storage import load_profiles


def get_tags_path() -> Path:
    from envswitch.storage import get_profiles_path
    return get_profiles_path().parent / "tags.json"


def load_tags(path: Path | None = None) -> Dict[str, List[str]]:
    p = path or get_tags_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(v, list)}


def save_tags(tags: Dict[str, List[str]], path: Path | None = None) -> None:
    p = path or get_tags_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(tags, indent=2))


def add_tag(profile: str, tag: str, path: Path | None = None) -> None:
    profiles = load_profiles()
    if profile not in profiles:
        raise KeyError(f"Profile '{profile}' not found")
    tags = load_tags(path)
    profile_tags = tags.get(profile, [])
    if tag not in profile_tags:
        profile_tags.append(tag)
    tags[profile] = profile_tags
    save_tags(tags, path)


def remove_tag(profile: str, tag: str, path: Path | None = None) -> None:
    tags = load_tags(path)
    profile_tags = tags.get(profile, [])
    tags[profile] = [t for t in profile_tags if t != tag]
    save_tags(tags, path)


def get_tags(profile: str, path: Path | None = None) -> List[str]:
    return load_tags(path).get(profile, [])


def find_by_tag(tag: str, path: Path | None = None) -> List[str]:
    tags = load_tags(path)
    return [profile for profile, ptags in tags.items() if tag in ptags]
