"""Clone a profile with variable overrides applied."""

from envswitch.storage import load_profiles, save_profiles


class ProfileNotFoundError(Exception):
    pass


class ProfileAlreadyExistsError(Exception):
    pass


def clone_profile(source: str, destination: str, overrides: dict[str, str], overwrite: bool = False) -> dict:
    """Clone a profile into a new profile, applying optional variable overrides.

    Args:
        source: Name of the profile to clone.
        destination: Name of the new profile.
        overrides: Key-value pairs to override in the cloned profile.
        overwrite: If True, overwrite destination if it exists.

    Returns:
        The newly created profile dict.
    """
    profiles = load_profiles()

    if source not in profiles:
        raise ProfileNotFoundError(f"Profile '{source}' not found.")

    if destination in profiles and not overwrite:
        raise ProfileAlreadyExistsError(f"Profile '{destination}' already exists.")

    cloned = dict(profiles[source])
    cloned.update(overrides)

    profiles[destination] = cloned
    save_profiles(profiles)

    return cloned
