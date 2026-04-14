"""Profile merging utilities for envswitch."""

from typing import Optional
from envswitch.storage import load_profiles, save_profiles


class ProfileNotFoundError(Exception):  # noqa: N818
    pass


class ProfileAlreadyExistsError(Exception):  # noqa: N818
    pass


def merge_profiles(
    source_names: list[str],
    destination: str,
    overwrite: bool = False,
    profiles_path: Optional[str] = None,
) -> dict:
    """Merge two or more profiles into a new destination profile.

    Variables from later source profiles override earlier ones on conflict.

    Args:
        source_names: Ordered list of profile names to merge.
        destination: Name of the resulting merged profile.
        overwrite: If True, overwrite destination if it already exists.
        profiles_path: Optional path to profiles file (for testing).

    Returns:
        The merged variable dictionary.

    Raises:
        ProfileNotFoundError: If any source profile does not exist.
        ProfileAlreadyExistsError: If destination exists and overwrite is False.
    """
    profiles = load_profiles(profiles_path)

    for name in source_names:
        if name not in profiles:
            raise ProfileNotFoundError(f"Profile '{name}' not found.")

    if destination in profiles and not overwrite:
        raise ProfileAlreadyExistsError(
            f"Profile '{destination}' already exists. Use --overwrite to replace it."
        )

    merged: dict = {}
    for name in source_names:
        merged.update(profiles[name])

    profiles[destination] = merged
    save_profiles(profiles, profiles_path)
    return merged
