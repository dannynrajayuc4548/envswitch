"""Search for environment variable keys or values across profiles."""

from typing import Dict, List, Tuple
from envswitch.storage import load_profiles


def search_profiles(
    query: str,
    search_keys: bool = True,
    search_values: bool = True,
    case_sensitive: bool = False,
) -> Dict[str, List[Tuple[str, str]]]:
    """Search all profiles for matching keys or values.

    Returns a dict mapping profile name to list of (key, value) matches.
    """
    profiles = load_profiles()
    results: Dict[str, List[Tuple[str, str]]] = {}

    needle = query if case_sensitive else query.lower()

    for profile_name, variables in profiles.items():
        matches: List[Tuple[str, str]] = []
        for key, value in variables.items():
            key_hit = search_keys and needle in (key if case_sensitive else key.lower())
            value_hit = search_values and needle in (value if case_sensitive else value.lower())
            if key_hit or value_hit:
                matches.append((key, value))
        if matches:
            results[profile_name] = matches

    return results


def search_in_profile(
    profile_name: str,
    query: str,
    search_keys: bool = True,
    search_values: bool = True,
    case_sensitive: bool = False,
) -> List[Tuple[str, str]]:
    """Search within a single profile. Returns list of (key, value) matches."""
    profiles = load_profiles()
    if profile_name not in profiles:
        raise KeyError(f"Profile '{profile_name}' not found.")

    needle = query if case_sensitive else query.lower()
    matches: List[Tuple[str, str]] = []

    for key, value in profiles[profile_name].items():
        key_hit = search_keys and needle in (key if case_sensitive else key.lower())
        value_hit = search_values and needle in (value if case_sensitive else value.lower())
        if key_hit or value_hit:
            matches.append((key, value))

    return matches
