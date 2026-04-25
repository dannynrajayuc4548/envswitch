"""CLI commands for managing profile TTLs."""

from __future__ import annotations

import time
from datetime import datetime

import click

from envswitch.storage import load_profiles
from envswitch.ttl import TTLError, get_expiry, is_expired, load_ttl, remove_ttl, set_ttl


@click.group(name="ttl")
def ttl_cmd() -> None:
    """Manage time-to-live expiry for profiles."""


@ttl_cmd.command("set")
@click.argument("profile")
@click.argument("seconds", type=float)
def ttl_set(profile: str, seconds: float) -> None:
    """Set a TTL of SECONDS for PROFILE."""
    profiles = load_profiles()
    if profile not in profiles:
        raise click.ClickException(f"Profile '{profile}' not found.")
    try:
        set_ttl(profile, seconds)
    except TTLError as exc:
        raise click.ClickException(str(exc)) from exc
    expiry = datetime.fromtimestamp(time.time() + seconds).strftime("%Y-%m-%d %H:%M:%S")
    click.echo(f"TTL set for '{profile}': expires at {expiry}")


@ttl_cmd.command("remove")
@click.argument("profile")
def ttl_remove(profile: str) -> None:
    """Remove the TTL for PROFILE."""
    remove_ttl(profile)
    click.echo(f"TTL removed for '{profile}'.")


@ttl_cmd.command("show")
@click.argument("profile")
def ttl_show(profile: str) -> None:
    """Show the TTL status for PROFILE."""
    expiry = get_expiry(profile)
    if expiry is None:
        click.echo(f"No TTL set for '{profile}'.")
        return
    expired = time.time() >= expiry
    ts = datetime.fromtimestamp(expiry).strftime("%Y-%m-%d %H:%M:%S")
    status = "EXPIRED" if expired else "active"
    click.echo(f"Profile '{profile}': expires {ts} [{status}]")


@ttl_cmd.command("list")
def ttl_list() -> None:
    """List all profiles with a TTL."""
    ttl = load_ttl()
    if not ttl:
        click.echo("No TTLs configured.")
        return
    now = time.time()
    for profile, expiry in sorted(ttl.items()):
        ts = datetime.fromtimestamp(expiry).strftime("%Y-%m-%d %H:%M:%S")
        status = "EXPIRED" if now >= expiry else "active"
        click.echo(f"  {profile}: {ts} [{status}]")
