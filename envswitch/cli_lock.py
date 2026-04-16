"""CLI commands for profile locking."""

import click
from envswitch.lock import (
    lock_profile,
    unlock_profile,
    is_locked,
    get_locked_profiles,
)
from envswitch.storage import load_profiles


@click.group("lock")
def lock_cmd():
    """Lock or unlock profiles to prevent modification."""


@lock_cmd.command("add")
@click.argument("profile")
def lock_add(profile: str):
    """Lock a profile."""
    profiles = load_profiles()
    if profile not in profiles:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    if is_locked(profile):
        click.echo(f"Profile '{profile}' is already locked.")
        return
    lock_profile(profile)
    click.echo(f"Profile '{profile}' locked.")


@lock_cmd.command("remove")
@click.argument("profile")
def lock_remove(profile: str):
    """Unlock a profile."""
    if not is_locked(profile):
        click.echo(f"Profile '{profile}' is not locked.")
        return
    unlock_profile(profile)
    click.echo(f"Profile '{profile}' unlocked.")


@lock_cmd.command("list")
def lock_list():
    """List all locked profiles."""
    locked = get_locked_profiles()
    if not locked:
        click.echo("No locked profiles.")
        return
    for name in locked:
        click.echo(name)


@lock_cmd.command("status")
@click.argument("profile")
def lock_status(profile: str):
    """Check if a profile is locked."""
    if is_locked(profile):
        click.echo(f"Profile '{profile}' is locked.")
    else:
        click.echo(f"Profile '{profile}' is not locked.")
