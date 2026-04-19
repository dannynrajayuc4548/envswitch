"""Profile inheritance: create profiles that extend a base profile."""

from envswitch.storage import load_profiles, save_profiles, get_profile


class ProfileNotFoundError(Exception):
    pass


class CircularInheritanceError(Exception):
    pass


def resolve_profile(profile_name: str, profiles: dict, _seen: set = None) -> dict:
    """Resolve a profile by merging base profile variables with overrides."""
    if _seen is None:
        _seen = set()
    if profile_name in _seen:
        raise CircularInheritanceError(
            f"Circular inheritance detected involving '{profile_name}'"
        )
    if profile_name not in profiles:
        raise ProfileNotFoundError(f"Profile '{profile_name}' not found")

    profile = profiles[profile_name]
    base_name = profile.get("__base__")
    own_vars = {k: v for k, v in profile.items() if k != "__base__"}

    if not base_name:
        return dict(own_vars)

    if base_name not in profiles:
        raise ProfileNotFoundError(f"Base profile '{base_name}' not found")

    _seen = _seen | {profile_name}
    base_vars = resolve_profile(base_name, profiles, _seen)
    base_vars.update(own_vars)
    return base_vars


def set_base(profile_name: str, base_name: str) -> None:
    """Set the base (parent) profile for a given profile."""
    profiles = load_profiles()
    if profile_name not in profiles:
        raise ProfileNotFoundError(f"Profile '{profile_name}' not found")
    if base_name not in profiles:
        raise ProfileNotFoundError(f"Base profile '{base_name}' not found")
    # Check for circular reference before saving
    profiles[profile_name]["__base__"] = base_name
    resolve_profile(profile_name, profiles)  # raises if circular
    save_profiles(profiles)


def remove_base(profile_name: str) -> None:
    """Remove the base profile link from a profile."""
    profiles = load_profiles()
    if profile_name not in profiles:
        raise ProfileNotFoundError(f"Profile '{profile_name}' not found")
    profiles[profile_name].pop("__base__", None)
    save_profiles(profiles)


def get_resolved(profile_name: str) -> dict:
    """Return fully resolved variables for a profile (with inheritance applied)."""
    profiles = load_profiles()
    return resolve_profile(profile_name, profiles)
