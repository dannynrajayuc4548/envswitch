"""Check which profiles match the current environment variables."""

import os
from typing import Dict, List, Tuple

from envswitch.storage import load_profiles


def get_current_env() -> Dict[str, str]:
    """Return a snapshot of the current environment variables."""
    return dict(os.environ)


def score_profile(profile_vars: Dict[str, str], env: Dict[str, str]) -> Tuple[int, int]:
    """Return (matching_count, total_count) for a profile against env."""
    total = len(profile_vars)
    if total == 0:
        return 0, 0
    matching = sum(
        1 for k, v in profile_vars.items() if env.get(k) == v
    )
    return matching, total


def check_profiles(
    env: Dict[str, str] | None = None,
    threshold: float = 1.0,
) -> List[Dict]:
    """
    Compare all profiles against the given (or current) environment.

    Returns a list of result dicts sorted by match ratio descending:
      {
        'name': str,
        'matching': int,
        'total': int,
        'ratio': float,
        'exact': bool,
      }

    Only profiles with ratio >= threshold are included.
    """
    if env is None:
        env = get_current_env()

    profiles = load_profiles()
    results = []

    for name, vars_ in profiles.items():
        matching, total = score_profile(vars_, env)
        ratio = (matching / total) if total > 0 else 0.0
        if ratio >= threshold:
            results.append(
                {
                    "name": name,
                    "matching": matching,
                    "total": total,
                    "ratio": ratio,
                    "exact": matching == total and total > 0,
                }
            )

    results.sort(key=lambda r: r["ratio"], reverse=True)
    return results
