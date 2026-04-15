"""Track history of profile switches per project directory."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


DEFAULT_HISTORY_SIZE = 20


def get_history_path() -> Path:
    """Return path to the history file."""
    config_dir = Path.home() / ".config" / "envswitch"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "history.json"


def load_history(path: Optional[Path] = None) -> dict:
    """Load history from disk, returning empty dict on missing or invalid file."""
    history_path = path or get_history_path()
    if not history_path.exists():
        return {}
    try:
        data = json.loads(history_path.read_text())
        if not isinstance(data, dict):
            return {}
        return data
    except (json.JSONDecodeError, OSError):
        return {}


def save_history(history: dict, path: Optional[Path] = None) -> None:
    """Persist history to disk."""
    history_path = path or get_history_path()
    history_path.write_text(json.dumps(history, indent=2))


def record_switch(
    profile_name: str,
    cwd: Optional[str] = None,
    path: Optional[Path] = None,
    max_entries: int = DEFAULT_HISTORY_SIZE,
) -> None:
    """Record a profile switch event for the given directory."""
    directory = cwd or str(Path.cwd())
    history = load_history(path)
    entries = history.get(directory, [])
    entries.append({
        "profile": profile_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    history[directory] = entries[-max_entries:]
    save_history(history, path)


def get_history(
    cwd: Optional[str] = None,
    path: Optional[Path] = None,
) -> list:
    """Return switch history entries for the given directory."""
    directory = cwd or str(Path.cwd())
    history = load_history(path)
    return history.get(directory, [])


def clear_history(
    cwd: Optional[str] = None,
    path: Optional[Path] = None,
) -> None:
    """Clear history for a specific directory, or all history if cwd is None."""
    if cwd is None:
        save_history({}, path)
    else:
        history = load_history(path)
        history.pop(cwd, None)
        save_history(history, path)
