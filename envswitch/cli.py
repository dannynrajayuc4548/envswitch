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


@click.group()
def cli():
    """envswitch — manage named environment variable profiles."""
    pass


@cli.command(name="list")
def list_cmd():
    """List all profiles."""
    profiles = load_profiles()
    if not profiles:
        click.echo("No profiles found.")
        return
    for name in sorted(profiles):
        click.echo(name)


@cli.command(name="show")
@click.argument("profile")
def show_cmd(profile):
    """Show variables in a profile."""
    data = get_profile(profile)
    if data is None:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    for k, v in sorted(data.items()):
        click.echo(f"{k}={v}")


@cli.command(name="set")
@click.argument("profile")
@click.argument("var")
@click.argument("value")
def set_cmd(profile, var, value):
    """Set a variable in a profile."""
    set_profile(profile, var, value)
    click.echo(f"Set {var} in '{profile}'.")


@cli.command(name="delete")
@click.argument("profile")
@click.option("--yes", is_flag=True, help="Skip confirmation.")
def delete_cmd(profile, yes):
    """Delete a profile."""
    if not yes:
        click.confirm(f"Delete profile '{profile}'?", abort=True)
    profiles = load_profiles()
    if profile not in profiles:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    del profiles[profile]
    save_profiles(profiles)
    click.echo(f"Deleted profile '{profile}'.")


cli.add_command(export_cmd, name="export")
cli.add_command(copy_cmd, name="copy")
cli.add_command(rename_cmd, name="rename")
cli.add_command(merge_cmd, name="merge")
cli.add_command(validate_cmd, name="validate")
cli.add_command(history_cmd, name="history")
cli.add_command(diff_cmd, name="diff")
cli.add_command(lock_cmd, name="lock")
cli.add_command(snapshot_cmd, name="snapshot")
cli.add_command(tag_cmd, name="tag")
cli.add_command(compare_cmd, name="compare")
