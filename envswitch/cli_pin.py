"""CLI commands for managing directory-pinned profiles."""

import click
from envswitch.pin import write_pin, read_pin, remove_pin, PinNotFoundError
from envswitch.storage import load_profiles


@click.group("pin")
def pin_cmd():
    """Pin a profile as default for the current directory."""


@pin_cmd.command("set")
@click.argument("profile")
@click.option("--dir", "directory", default=None, help="Target directory (default: cwd)")
def pin_set(profile, directory):
    """Pin PROFILE as the default for a directory."""
    profiles = load_profiles()
    if profile not in profiles:
        click.echo(f"Error: profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    path = write_pin(profile, directory)
    click.echo(f"Pinned '{profile}' in {path.parent}")


@pin_cmd.command("show")
@click.option("--dir", "directory", default=None, help="Target directory (default: cwd)")
def pin_show(directory):
    """Show the pinned profile for a directory."""
    profile = read_pin(directory)
    if profile is None:
        click.echo("No profile pinned in this directory.")
    else:
        click.echo(profile)


@pin_cmd.command("remove")
@click.option("--dir", "directory", default=None, help="Target directory (default: cwd)")
def pin_remove(directory):
    """Remove the pinned profile for a directory."""
    try:
        remove_pin(directory)
        click.echo("Pin removed.")
    except PinNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
