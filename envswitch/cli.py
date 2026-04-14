"""CLI entry point for envswitch."""

import click
from envswitch.storage import (
    load_profiles,
    save_profiles,
    get_profile,
    set_profile,
    delete_profile,
    list_profiles,
)


@click.group()
def cli():
    """envswitch — quickly switch between named environment variable profiles."""
    pass


@cli.command("list")
def list_cmd():
    """List all available profiles."""
    profiles = list_profiles()
    if not profiles:
        click.echo("No profiles found.")
        return
    for name in profiles:
        click.echo(name)


@cli.command("show")
@click.argument("profile_name")
def show_cmd(profile_name):
    """Show all environment variables in a profile."""
    profile = get_profile(profile_name)
    if profile is None:
        click.echo(f"Profile '{profile_name}' not found.", err=True)
        raise SystemExit(1)
    for key, value in sorted(profile.items()):
        click.echo(f"{key}={value}")


@cli.command("set")
@click.argument("profile_name")
@click.argument("key")
@click.argument("value")
def set_cmd(profile_name, key, value):
    """Set a variable in a profile (creates profile if it doesn't exist)."""
    profiles = load_profiles()
    if profile_name not in profiles:
        profiles[profile_name] = {}
    profiles[profile_name][key] = value
    save_profiles(profiles)
    click.echo(f"Set {key}={value} in profile '{profile_name}'.")


@cli.command("delete")
@click.argument("profile_name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def delete_cmd(profile_name, yes):
    """Delete a profile entirely."""
    if not yes:
        click.confirm(f"Delete profile '{profile_name}'?", abort=True)
    deleted = delete_profile(profile_name)
    if not deleted:
        click.echo(f"Profile '{profile_name}' not found.", err=True)
        raise SystemExit(1)
    click.echo(f"Profile '{profile_name}' deleted.")


@cli.command("export")
@click.argument("profile_name")
@click.option("--shell", default="bash", type=click.Choice(["bash", "fish"]), help="Shell syntax.")
def export_cmd(profile_name, shell):
    """Print export statements for a profile (eval-friendly)."""
    profile = get_profile(profile_name)
    if profile is None:
        click.echo(f"Profile '{profile_name}' not found.", err=True)
        raise SystemExit(1)
    for key, value in sorted(profile.items()):
        if shell == "fish":
            click.echo(f"set -x {key} {value}")
        else:
            click.echo(f"export {key}={value}")


if __name__ == "__main__":
    cli()
