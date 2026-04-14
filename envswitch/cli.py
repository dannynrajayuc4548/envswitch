"""Main CLI entry point for envswitch."""

import click
from envswitch.storage import load_profiles, save_profiles, get_profile, set_profile, delete_profile
from envswitch.cli_export import export_cmd


@click.group()
@click.version_option()
def cli() -> None:
    """envswitch — quickly switch between named environment variable profiles."""


@cli.command("list")
def list_cmd() -> None:
    """List all available profiles."""
    profiles = load_profiles()
    if not profiles:
        click.echo("No profiles found.")
        return
    for name in sorted(profiles):
        count = len(profiles[name])
        click.echo(f"  {name} ({count} var{'s' if count != 1 else ''})")


@cli.command("show")
@click.argument("profile_name")
def show_cmd(profile_name: str) -> None:
    """Show all variables in a profile."""
    profile = get_profile(profile_name)
    if profile is None:
        raise click.ClickException(f"Profile '{profile_name}' not found.")
    if not profile:
        click.echo(f"Profile '{profile_name}' is empty.")
        return
    for key, value in sorted(profile.items()):
        click.echo(f"  {key}={value}")


@cli.command("set")
@click.argument("profile_name")
@click.argument("key")
@click.argument("value")
def set_cmd(profile_name: str, key: str, value: str) -> None:
    """Set a variable in a profile."""
    set_profile(profile_name, key, value)
    click.echo(f"Set {key}={value} in profile '{profile_name}'.")


@cli.command("delete")
@click.argument("profile_name")
@click.option("--key", "-k", default=None, help="Delete a specific key instead of the whole profile.")
def delete_cmd(profile_name: str, key: str) -> None:
    """Delete a profile or a specific key within a profile."""
    profiles = load_profiles()
    if profile_name not in profiles:
        raise click.ClickException(f"Profile '{profile_name}' not found.")
    if key:
        if key not in profiles[profile_name]:
            raise click.ClickException(f"Key '{key}' not found in profile '{profile_name}'.")
        del profiles[profile_name][key]
        save_profiles(profiles)
        click.echo(f"Deleted key '{key}' from profile '{profile_name}'.")
    else:
        delete_profile(profile_name)
        click.echo(f"Deleted profile '{profile_name}'.")


cli.add_command(export_cmd)


if __name__ == "__main__":
    cli()
