"""Bookmark support: save named shortcuts to profiles with optional descriptions."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from envswitch.storage import load_profiles


class BookmarkError(Exception):
    pass


def get_bookmarks_path() -> Path:
    from envswitch.storage import get_profiles_path
    return get_profiles_path().parent / "bookmarks.json"


def load_bookmarks(path: Optional[Path] = None) -> Dict[str, dict]:
    p = path or get_bookmarks_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def save_bookmarks(bookmarks: Dict[str, dict], path: Optional[Path] = None) -> None:
    p = path or get_bookmarks_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(bookmarks, indent=2))


def add_bookmark(
    name: str,
    profile: str,
    description: str = "",
    path: Optional[Path] = None,
) -> None:
    profiles = load_profiles()
    if profile not in profiles:
        raise BookmarkError(f"Profile '{profile}' does not exist.")
    bookmarks = load_bookmarks(path)
    if name in bookmarks:
        raise BookmarkError(f"Bookmark '{name}' already exists. Use --force to overwrite.")
    bookmarks[name] = {"profile": profile, "description": description}
    save_bookmarks(bookmarks, path)


def remove_bookmark(name: str, path: Optional[Path] = None) -> None:
    bookmarks = load_bookmarks(path)
    if name not in bookmarks:
        raise BookmarkError(f"Bookmark '{name}' not found.")
    del bookmarks[name]
    save_bookmarks(bookmarks, path)


def get_bookmark(name: str, path: Optional[Path] = None) -> dict:
    bookmarks = load_bookmarks(path)
    if name not in bookmarks:
        raise BookmarkError(f"Bookmark '{name}' not found.")
    return bookmarks[name]


def list_bookmarks(path: Optional[Path] = None) -> List[dict]:
    bookmarks = load_bookmarks(path)
    return [
        {"name": k, "profile": v["profile"], "description": v.get("description", "")}
        for k, v in bookmarks.items()
    ]
