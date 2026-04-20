"""Per-profile notes/comments storage."""

import json
from pathlib import Path
from envswitch.storage import load_profiles


def get_notes_path() -> Path:
    from envswitch.storage import get_profiles_path
    return get_profiles_path().parent / "notes.json"


def load_notes() -> dict:
    path = get_notes_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            return {}
        return data
    except (json.JSONDecodeError, OSError):
        return {}


def save_notes(notes: dict) -> None:
    path = get_notes_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notes, indent=2))


def set_note(profile: str, note: str) -> None:
    profiles = load_profiles()
    if profile not in profiles:
        raise KeyError(f"Profile '{profile}' not found.")
    notes = load_notes()
    notes[profile] = note
    save_notes(notes)


def get_note(profile: str) -> str | None:
    notes = load_notes()
    return notes.get(profile)


def remove_note(profile: str) -> None:
    notes = load_notes()
    if profile not in notes:
        raise KeyError(f"No note for profile '{profile}'.")
    del notes[profile]
    save_notes(notes)


def list_notes() -> dict:
    return load_notes()
