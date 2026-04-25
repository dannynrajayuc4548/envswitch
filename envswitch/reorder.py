"""Reorder variables within a profile."""

from envswitch.storage import load_profiles, save_profiles


class ProfileNotFoundError(Exception):
    pass


class ReorderError(Exception):
    pass


def reorder_profile(profile_name: str, key_order: list[str], fill_missing: bool = True) -> dict:
    """Reorder the keys of a profile according to key_order.

    Args:
        profile_name: The profile to reorder.
        key_order: Desired key ordering. Keys not listed are appended at the end
                   unless fill_missing is False, in which case they are dropped.
        fill_missing: If True, keys not in key_order are appended at the end.

    Returns:
        The reordered profile dict.

    Raises:
        ProfileNotFoundError: If the profile does not exist.
        ReorderError: If key_order contains keys not present in the profile.
    """
    profiles = load_profiles()
    if profile_name not in profiles:
        raise ProfileNotFoundError(f"Profile '{profile_name}' not found.")

    profile = profiles[profile_name]
    unknown = [k for k in key_order if k not in profile]
    if unknown:
        raise ReorderError(
            f"Keys not found in profile '{profile_name}': {', '.join(unknown)}"
        )

    reordered = {k: profile[k] for k in key_order if k in profile}
    if fill_missing:
        for k, v in profile.items():
            if k not in reordered:
                reordered[k] = v

    profiles[profile_name] = reordered
    save_profiles(profiles)
    return reordered


def move_key(profile_name: str, key: str, position: int) -> dict:
    """Move a single key to a specific position (0-indexed) within the profile.

    Returns the reordered profile dict.
    """
    profiles = load_profiles()
    if profile_name not in profiles:
        raise ProfileNotFoundError(f"Profile '{profile_name}' not found.")

    profile = profiles[profile_name]
    if key not in profile:
        raise ReorderError(f"Key '{key}' not found in profile '{profile_name}'.")

    keys = [k for k in profile if k != key]
    position = max(0, min(position, len(keys)))
    keys.insert(position, key)

    reordered = {k: profile[k] for k in keys}
    profiles[profile_name] = reordered
    save_profiles(profiles)
    return reordered
