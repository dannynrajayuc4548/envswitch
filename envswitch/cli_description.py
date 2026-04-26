"""CLI commands for managing profile descriptions."""

from __future__ import annotations

import click

from envswitch.description import (
    get_description,
    list_descriptions,
    remove_description,
    set_description,
)


@click.group("description", help="Manage human-readable descriptions for profiles.")
def description_cmd() -> None:
    pass


@description_cmd.command("set")
@click.argument("profile")
@click.argument("text")
def desc_set(profile: str, text: str) -> None:
    """Set a description for PROFILE."""
    try:
        set_description(profile, text)
        click.echo(f"Description set for '{profile}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@description_cmd.command("show")
@click.argument("profile")
def desc_show(profile: str) -> None:
    """Show the description for PROFILE."""
    desc = get_description(profile)
    if desc is None:
        click.echo(f"No description set for '{profile}'.")
    else:
        click.echo(desc)


@description_cmd.command("remove")
@click.argument("profile")
def desc_remove(profile: str) -> None:
    """Remove the description for PROFILE."""
    removed = remove_description(profile)
    if removed:
        click.echo(f"Description removed for '{profile}'.")
    else:
        click.echo(f"No description found for '{profile}'.")


@description_cmd.command("list")
def desc_list() -> None:
    """List all profiles that have descriptions."""
    descs = list_descriptions()
    if not descs:
        click.echo("No descriptions set.")
        return
    for profile, text in sorted(descs.items()):
        click.echo(f"{profile}: {text}")
