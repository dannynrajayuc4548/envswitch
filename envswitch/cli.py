"""Main CLI entry point for envswitch."""

import click
from envswitch.storage import load_profiles, save_profiles, get_profile, set_profile, delete_profile
from envswitch.cli_export import export_cmd
from envswitch.cli_copy import copy_cmd, rename_cmd
from envswitch.cli_merge import merge_cmd
from envswitch.cli_validate import validate_cmd
from envswitch.cli_history import history_cmd
from envswitch.diff_cli import diff_cmd
from envswitch.cli_lock import lock_cmd
from envswitch.cli_snapshot import snapshot_cmd
from envswitch.cli_tag import tag_cmd
from envswitch.cli_compare import compare_cmd
from envswitch.cli_pin import pin_cmd
from envswitch.cli_import_export import file_cmd
from envswitch.cli_schedule import schedule_cmd


@click.group()
def cli():
    """envswitch — manage environment variable profiles."""


@cli.command("list")
def list_cmd():
    """List all profiles."""
    profiles = load_profiles()
    if not profiles:
        click.echo("No profiles found.")
        return
    for name in profiles:
        click.echo(name)


@cli.command("show")
@click.argument("profile")
def show_cmd(profile):
    """Show variables in a profile."""
    data = get_profile(profile)
    if data is None:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    for key, value in data.items():
        click.echo(f"{key}={value}")


@cli.command("set")
@click.argument("profile")
@click.argument("key")
@click.argument("value")
def set_cmd(profile, key, value):
    """Set a variable in a profile."""
    set_profile(profile, key, value)
    click.echo(f"Set {key}={value} in profile '{profile}'.")


@cli.command("delete")
@click.argument("profile")
def delete_cmd(profile):
    """Delete a profile."""
    profiles = load_profiles()
    if profile not in profiles:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    delete_profile(profile)
    click.echo(f"Deleted profile '{profile}'.")


cli.add_command(export_cmd, "export")
cli.add_command(copy_cmd, "copy")
cli.add_command(rename_cmd, "rename")
cli.add_command(merge_cmd, "merge")
cli.add_command(validate_cmd, "validate")
cli.add_command(history_cmd, "history")
cli.add_command(diff_cmd, "diff")
cli.add_command(lock_cmd, "lock")
cli.add_command(snapshot_cmd, "snapshot")
cli.add_command(tag_cmd, "tag")
cli.add_command(compare_cmd, "compare")
cli.add_command(pin_cmd, "pin")
cli.add_command(file_cmd, "file")
cli.add_command(schedule_cmd, "schedule")
