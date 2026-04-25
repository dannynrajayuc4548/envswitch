"""TTL (time-to-live) support for environment profiles."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Optional

from envswitch.storage import get_profiles_path


class TTLError(Exception):
    """Raised when a TTL operation fails."""


def get_ttl_path() -> Path:
    return get_profiles_path().parent / "ttl.json"


def load_ttl() -> Dict[str, float]:
    path = get_ttl_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: float(v) for k, v in data.items() if isinstance(v, (int, float))}


def save_ttl(ttl: Dict[str, float]) -> None:
    path = get_ttl_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ttl, indent=2))


def set_ttl(profile: str, seconds: float) -> None:
    """Set a TTL for *profile*; it expires *seconds* from now."""
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")
    ttl = load_ttl()
    ttl[profile] = time.time() + seconds
    save_ttl(ttl)


def remove_ttl(profile: str) -> None:
    """Remove any TTL entry for *profile*."""
    ttl = load_ttl()
    ttl.pop(profile, None)
    save_ttl(ttl)


def get_expiry(profile: str) -> Optional[float]:
    """Return the UNIX timestamp when *profile* expires, or None."""
    return load_ttl().get(profile)


def is_expired(profile: str) -> bool:
    """Return True if *profile* has a TTL that has already passed."""
    expiry = get_expiry(profile)
    if expiry is None:
        return False
    return time.time() >= expiry


def purge_expired(profiles: Dict) -> list[str]:
    """Remove expired profiles from *profiles* dict in-place; return purged names."""
    ttl = load_ttl()
    now = time.time()
    purged = [name for name, exp in ttl.items() if now >= exp and name in profiles]
    for name in purged:
        del profiles[name]
        ttl.pop(name, None)
    save_ttl(ttl)
    return purged
