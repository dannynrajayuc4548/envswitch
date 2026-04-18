"""Schedule-based automatic profile switching."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
from datetime import time

SCHEDULE_FILE = "schedules.json"


def get_schedule_path() -> Path:
    from envswitch.storage import get_profiles_path
    return get_profiles_path().parent / SCHEDULE_FILE


def load_schedules() -> dict:
    path = get_schedule_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            return {}
        return data
    except (json.JSONDecodeError, ValueError):
        return {}


def save_schedules(schedules: dict) -> None:
    path = get_schedule_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(schedules, indent=2))


def add_schedule(profile: str, start: str, end: str, days: Optional[list[str]] = None) -> None:
    """Add or update a schedule for a profile."""
    from envswitch.storage import get_profile
    if get_profile(profile) is None:
        raise ValueError(f"Profile '{profile}' not found.")
    # Validate time format
    time.fromisoformat(start)
    time.fromisoformat(end)
    schedules = load_schedules()
    schedules[profile] = {"start": start, "end": end, "days": days or []}
    save_schedules(schedules)


def remove_schedule(profile: str) -> None:
    schedules = load_schedules()
    if profile not in schedules:
        raise KeyError(f"No schedule found for profile '{profile}'.")
    del schedules[profile]
    save_schedules(schedules)


def get_schedule(profile: str) -> Optional[dict]:
    return load_schedules().get(profile)


def get_active_profile(now: Optional[object] = None) -> Optional[str]:
    """Return the first profile whose schedule matches the current time."""
    from datetime import datetime
    if now is None:
        now = datetime.now()
    current_time = now.time().replace(second=0, microsecond=0)
    day_name = now.strftime("%A").lower()
    for profile, sched in load_schedules().items():
        start = time.fromisoformat(sched["start"])
        end = time.fromisoformat(sched["end"])
        days = [d.lower() for d in sched.get("days", [])]
        if days and day_name not in days:
            continue
        if start <= current_time <= end:
            return profile
    return None
