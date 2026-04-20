"""CLI commands for profile inheritance management."""

import click
from envswitch.inherit import (
    ProfileNotFoundError,
    CircularInheritanceError,
    resolve_profile,
    set_base,
    remove_base,
    get_base,
)
from envswitch.storage import load_profiles


@click.group(name="inherit")
def inherit_cmd():
    """Manage profile inheritance."""


@inherit_cmd.command(name="set")
@click.argument("profile")
@click.argument("base")
def inherit_set(profile, base):
    """Set BASE as the parent profile for PROFILE."""
    try:
        set_base(profile, base)
        click.echo(f"Profile '{profile}' now inherits from '{base}'.")
    except ProfileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except CircularInheritanceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@inherit_cmd.command(name="remove")
@click.argument("profile")
def inherit_remove(profile):
    """Remove inheritance from PROFILE."""
    try:
        remove_base(profile)
        click.echo(f"Inheritance removed from '{profile}'.")
    except ProfileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@inherit_cmd.command(name="show")
@click.argument("profile")
@click.option("--resolved", is_flag=True, help="Show fully resolved variables.")
def inherit_show(profile, resolved):
    """Show inheritance info for PROFILE."""
    try:
        base = get_base(profile)
        if resolved:
            vars_ = resolve_profile(profile)
            click.echo(f"Resolved variables for '{profile}':")
            for k, v in sorted(vars_.items()):
                click.echo(f"  {k}={v}")
        else:
            if base:
                click.echo(f"Profile '{profile}' inherits from '{base}'.")
            else:
                click.echo(f"Profile '{profile}' has no base profile.")
    except ProfileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except CircularInheritanceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@inherit_cmd.command(name="list")
def inherit_list():
    """List all profiles that have a base profile set."""
    profiles = load_profiles()
    found = False
    for name, data in sorted(profiles.items()):
        base = data.get("__base__") if isinstance(data, dict) else None
        if base:
            click.echo(f"  {name} -> {base}")
            found = True
    if not found:
        click.echo("No profiles with inheritance configured.")
