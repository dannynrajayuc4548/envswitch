"""Hook utilities that integrate TTL purging into the main CLI lifecycle."""

from __future__ import annotations

from typing import Dict

import click

from envswitch.storage import load_profiles, save_profiles
from envswitch.ttl import purge_expired


def run_ttl_purge(*, verbose: bool = False) -> list[str]:
    """Load profiles, purge any expired ones, persist changes, return purged names.

    This is intended to be called at the start of relevant CLI commands so that
    stale profiles are cleaned up transparently.
    """
    profiles: Dict = load_profiles()
    purged = purge_expired(profiles)
    if purged:
        save_profiles(profiles)
        if verbose:
            for name in purged:
                click.echo(f"[ttl] Profile '{name}' expired and was removed.", err=True)
    return purged


def ttl_purge_option(func):
    """Decorator that adds a --purge-expired flag and runs TTL purge when set."""

    @click.option(
        "--purge-expired",
        is_flag=True,
        default=False,
        help="Remove TTL-expired profiles before running this command.",
    )
    def wrapper(*args, purge_expired: bool = False, **kwargs):
        if purge_expired:
            removed = run_ttl_purge(verbose=True)
            if removed:
                click.echo(f"Purged {len(removed)} expired profile(s).", err=True)
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
