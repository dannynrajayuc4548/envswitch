"""CLI commands for profile alias management."""

import click
from envswitch.alias import add_alias, remove_alias, list_aliases, resolve_alias, AliasError


@click.group("alias")
def alias_cmd():
    """Manage profile aliases."""


@alias_cmd.command("add")
@click.argument("alias")
@click.argument("profile")
def alias_add(alias, profile):
    """Add an alias for a profile."""
    try:
        add_alias(alias, profile)
        click.echo(f"Alias '{alias}' -> '{profile}' added.")
    except AliasError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_cmd.command("remove")
@click.argument("alias")
def alias_remove(alias):
    """Remove an alias."""
    try:
        remove_alias(alias)
        click.echo(f"Alias '{alias}' removed.")
    except AliasError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_cmd.command("list")
def alias_list():
    """List all aliases."""
    aliases = list_aliases()
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, profile in sorted(aliases.items()):
        click.echo(f"  {alias} -> {profile}")


@alias_cmd.command("resolve")
@click.argument("alias")
def alias_resolve(alias):
    """Resolve an alias to its profile name."""
    profile = resolve_alias(alias)
    if profile is None:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    click.echo(profile)
