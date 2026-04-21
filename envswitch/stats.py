"""Profile usage statistics derived from audit and history logs."""

from collections import Counter
from typing import Dict, List, Optional

from envswitch.audit import load_audit
from envswitch.history import load_history


class StatsError(Exception):
    pass


def count_switches(profile_name: Optional[str] = None) -> Dict[str, int]:
    """Count how many times each profile (or a specific one) has been switched to."""
    history = load_history()
    entries = history.get("entries", [])
    if not isinstance(entries, list):
        raise StatsError("History entries are malformed.")

    counter: Counter = Counter()
    for entry in entries:
        name = entry.get("profile")
        if name:
            counter[name] += 1

    if profile_name is not None:
        return {profile_name: counter.get(profile_name, 0)}
    return dict(counter)


def most_used(top_n: int = 5) -> List[Dict]:
    """Return the top N most-used profiles by switch count."""
    counts = count_switches()
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"profile": name, "count": count} for name, count in ranked[:top_n]]


def audit_event_summary() -> Dict[str, int]:
    """Summarise audit events by event type."""
    audit = load_audit()
    entries = audit.get("entries", [])
    if not isinstance(entries, list):
        raise StatsError("Audit entries are malformed.")

    counter: Counter = Counter()
    for entry in entries:
        event = entry.get("event", "unknown")
        counter[event] += 1
    return dict(counter)


def profile_last_used(profile_name: str) -> Optional[str]:
    """Return the ISO timestamp of the last time a profile was switched to."""
    history = load_history()
    entries = history.get("entries", [])
    timestamps = [
        e.get("timestamp")
        for e in reversed(entries)
        if e.get("profile") == profile_name and e.get("timestamp")
    ]
    return timestamps[0] if timestamps else None
