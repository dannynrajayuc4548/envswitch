"""Main CLI entry point for envswitch."""

import click
from envswitch.storage import load_profiles, save_profiles, get_profile, set_profile, delete_profile
from envswitch.cli_export import export_cmd
from envswitch.cli_copy import copy_cmd, rename_cmd
from envswitch.cli_merge import merge_cmd
from envswitch.cli_validate import validate_cmd


@click.group()
def cli():
    """envswitch — quickly switch between named environment variable profiles."""
    pass


@cli.command("list")
def list_cmd():
    """List all available profiles."""
    profiles = load_profiles()
    if not profiles:
        click.echo("No profiles found.")
        return
    for name in profiles:
        click.echo(name)


@cli.command("show")
@click.argument("profile")
def show_cmd(profile: str):
    """Show all variables in a profile."""
    variables = get_profile(profile)
    if variables is None:
        click.echo(f"Profile {profile!r} not found.", err=True)
        raise SystemExit(1)
    for key, value in variables.items():
        click.echo(f"{key}={value}")


@cli.command("set")
@click.argument("profile")
@click.argument("key")
@click.argument("value")
def set_cmd(profile: str, key: str, value: str):
    """Set a variable in a profile."""
    set_profile(profile, key, value)
    click.echo(f"Set {key} in profile {profile!r}.")


@cli.command("delete")
@click.argument("profile")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def delete_cmd(profile: str, yes: bool):
    """Delete a profile."""
    if not yes:
        click.confirm(f"Delete profile {profile!r}?", abort=True)
    profiles = load_profiles()
    if profile not in profiles:
        click.echo(f"Profile {profile!r} not found.", err=True)
        raise SystemExit(1)
    del profiles[profile]
    save_profiles(profiles)
    click.echo(f"Deleted profile {profile!r}.")


cli.add_command(export_cmd)
cli.add_command(copy_cmd)
cli.add_command(rename_cmd)
cli.add_command(merge_cmd)
cli.add_command(validate_cmd)


if __name__ == "__main__":
    cli()
