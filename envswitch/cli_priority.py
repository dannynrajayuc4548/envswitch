"""CLI commands for managing profile priorities."""

from __future__ import annotations

import click

from envswitch.priority import (
    PriorityError,
    get_priority,
    list_by_priority,
    remove_priority,
    set_priority,
)


@click.group("priority")
def priority_cmd() -> None:
    """Manage profile priority levels."""


@priority_cmd.command("set")
@click.argument("profile")
@click.argument("level", type=int)
def priority_set(profile: str, level: int) -> None:
    """Assign a numeric LEVEL to PROFILE (higher = more important)."""
    try:
        set_priority(profile, level)
        click.echo(f"Priority for '{profile}' set to {level}.")
    except PriorityError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@priority_cmd.command("remove")
@click.argument("profile")
def priority_remove(profile: str) -> None:
    """Remove the priority level from PROFILE."""
    try:
        remove_priority(profile)
        click.echo(f"Priority removed from '{profile}'.")
    except PriorityError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@priority_cmd.command("show")
@click.argument("profile")
def priority_show(profile: str) -> None:
    """Show the priority level of PROFILE."""
    level = get_priority(profile)
    if level is None:
        click.echo(f"No priority set for '{profile}'.")
    else:
        click.echo(f"{profile}: {level}")


@priority_cmd.command("list")
def priority_list() -> None:
    """List all profiles with priorities, sorted highest first."""
    entries = list_by_priority()
    if not entries:
        click.echo("No priorities set.")
        return
    for name, level in entries:
        click.echo(f"{name}: {level}")
