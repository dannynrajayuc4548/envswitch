"""Diff two environment variable profiles."""

from typing import Dict, List, Tuple
from envswitch.storage import get_profile


class ProfileNotFoundError(Exception):
    pass


DiffResult = Dict[str, Dict[str, object]]


def diff_profiles(profile_a: str, profile_b: str, profiles: dict) -> DiffResult:
    """Compare two profiles and return a structured diff.

    Returns a dict with keys:
      - 'added':   vars in B but not in A
      - 'removed': vars in A but not in B
      - 'changed': vars in both but with different values
      - 'unchanged': vars with identical values in both
    """
    env_a = get_profile(profile_a, profiles)
    if env_a is None:
        raise ProfileNotFoundError(f"Profile '{profile_a}' not found.")

    env_b = get_profile(profile_b, profiles)
    if env_b is None:
        raise ProfileNotFoundError(f"Profile '{profile_b}' not found.")

    keys_a = set(env_a.keys())
    keys_b = set(env_b.keys())

    added = {k: env_b[k] for k in keys_b - keys_a}
    removed = {k: env_a[k] for k in keys_a - keys_b}
    changed = {
        k: {"from": env_a[k], "to": env_b[k]}
        for k in keys_a & keys_b
        if env_a[k] != env_b[k]
    }
    unchanged = {
        k: env_a[k]
        for k in keys_a & keys_b
        if env_a[k] == env_b[k]
    }

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def format_diff(result: DiffResult) -> List[str]:
    """Format a diff result as a list of human-readable lines."""
    lines: List[str] = []

    for key, value in sorted(result["added"].items()):
        lines.append(f"+ {key}={value}")

    for key, value in sorted(result["removed"].items()):
        lines.append(f"- {key}={value}")

    for key, info in sorted(result["changed"].items()):
        lines.append(f"~ {key}: {info['from']!r} -> {info['to']!r}")

    for key, value in sorted(result["unchanged"].items()):
        lines.append(f"  {key}={value}")

    return lines
