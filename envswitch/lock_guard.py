"""Guard utilities to enforce lock checks before profile mutations."""

import click
from functools import wraps
from envswitch.lock import is_locked, ProfileLockedError


def require_unlocked(profile_arg: str = "profile"):
    """Decorator for Click commands that checks a profile is not locked.

    The decorated command must have a parameter named `profile_arg`.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            profile = kwargs.get(profile_arg)
            if profile and is_locked(profile):
                raise ProfileLockedError(
                    f"Profile '{profile}' is locked. Unlock it first with: "
                    f"envswitch lock remove {profile}"
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def check_locked(profile: str) -> None:
    """Raise ProfileLockedError if profile is locked. Use in non-decorator contexts."""
    if is_locked(profile):
        raise ProfileLockedError(
            f"Profile '{profile}' is locked. Unlock it first with: "
            f"envswitch lock remove {profile}"
        )


def abort_if_locked(profile: str) -> None:
    """Print error and exit if profile is locked. Suitable for CLI command bodies."""
    if is_locked(profile):
        click.echo(
            f"Error: Profile '{profile}' is locked. "
            f"Run 'envswitch lock remove {profile}' to unlock.",
            err=True,
        )
        raise SystemExit(1)
