"""Promote a profile by merging a source profile's vars into a destination,
optionally overwriting existing keys."""

from envswitch.storage import load_profiles, save_profiles


class ProfileNotFoundError(Exception):
    pass


class PromoteError(Exception):
    pass


def promote_profile(
    source: str,
    destination: str,
    overwrite: bool = False,
    keys: list[str] | None = None,
) -> dict[str, str]:
    """Promote variables from *source* into *destination*.

    Args:
        source: Name of the profile to promote from.
        destination: Name of the profile to promote into.
        overwrite: If True, existing keys in destination are overwritten.
        keys: Optional list of specific variable names to promote.
              When None all variables are promoted.

    Returns:
        The updated destination profile dict.

    Raises:
        ProfileNotFoundError: If source or destination profile does not exist.
        PromoteError: If there are key conflicts and overwrite is False.
    """
    profiles = load_profiles()

    if source not in profiles:
        raise ProfileNotFoundError(f"Source profile '{source}' not found.")
    if destination not in profiles:
        raise ProfileNotFoundError(f"Destination profile '{destination}' not found.")

    src_vars: dict[str, str] = profiles[source]
    dst_vars: dict[str, str] = profiles[destination]

    to_promote = {k: v for k, v in src_vars.items() if keys is None or k in keys}

    if keys:
        missing = set(keys) - set(src_vars)
        if missing:
            raise PromoteError(
                f"Keys not found in source profile '{source}': {', '.join(sorted(missing))}"
            )

    if not overwrite:
        conflicts = set(to_promote) & set(dst_vars)
        if conflicts:
            raise PromoteError(
                f"Keys already exist in '{destination}': {', '.join(sorted(conflicts))}. "
                "Use --overwrite to replace them."
            )

    dst_vars.update(to_promote)
    profiles[destination] = dst_vars
    save_profiles(profiles)
    return dst_vars
