"""Profile copy/rename utilities for envswitch."""

from envswitch.storage import load_profiles, save_profiles


class ProfileNotFoundError(Exception):
    pass


class ProfileAlreadyExistsError(Exception):
    pass


def copy_profile(source: str, destination: str, overwrite: bool = False) -> None:
    """Copy a profile to a new name.

    Args:
        source: Name of the profile to copy.
        destination: Name of the new profile.
        overwrite: If True, overwrite destination if it exists.

    Raises:
        ProfileNotFoundError: If the source profile does not exist.
        ProfileAlreadyExistsError: If destination exists and overwrite is False.
    """
    profiles = load_profiles()

    if source not in profiles:
        raise ProfileNotFoundError(f"Profile '{source}' not found.")

    if destination in profiles and not overwrite:
        raise ProfileAlreadyExistsError(
            f"Profile '{destination}' already exists. Use --overwrite to replace it."
        )

    profiles[destination] = dict(profiles[source])
    save_profiles(profiles)


def rename_profile(source: str, destination: str, overwrite: bool = False) -> None:
    """Rename a profile.

    Args:
        source: Current name of the profile.
        destination: New name for the profile.
        overwrite: If True, overwrite destination if it exists.

    Raises:
        ProfileNotFoundError: If the source profile does not exist.
        ProfileAlreadyExistsError: If destination exists and overwrite is False.
    """
    copy_profile(source, destination, overwrite=overwrite)

    profiles = load_profiles()
    del profiles[source]
    save_profiles(profiles)
