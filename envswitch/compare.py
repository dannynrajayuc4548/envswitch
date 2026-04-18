"""Compare multiple profiles side by side."""
from typing import Dict, List, Tuple
from envswitch.storage import load_profiles


class ProfileNotFoundError(Exception):
    pass


def compare_profiles(profile_names: List[str]) -> Dict:
    """Compare multiple profiles, returning a unified view of all keys."""
    profiles = load_profiles()
    result = {}

    for name in profile_names:
        if name not in profiles:
            raise ProfileNotFoundError(f"Profile '{name}' not found.")

    all_keys = set()
    for name in profile_names:
        all_keys.update(profiles[name].keys())

    for key in sorted(all_keys):
        result[key] = {}
        for name in profile_names:
            result[key][name] = profiles[name].get(key, None)

    return result


def format_compare(comparison: Dict, profile_names: List[str]) -> str:
    """Format comparison result as a readable table."""
    if not comparison:
        return "No variables found."

    col_width = max(len(k) for k in comparison) + 2
    name_width = max(len(n) for n in profile_names) + 2

    header = f"{'KEY':<{col_width}}" + "".join(f"{n:<{name_width}}" for n in profile_names)
    lines = [header, "-" * len(header)]

    for key, values in comparison.items():
        row = f"{key:<{col_width}}"
        for name in profile_names:
            val = values[name]
            row += f"{(val if val is not None else '(missing)'):<{name_width}}"
        lines.append(row)

    return "\n".join(lines)
