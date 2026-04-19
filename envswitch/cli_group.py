"""CLI commands for profile groups."""
import click
from envswitch.group import (
    GroupError, add_to_group, remove_from_group,
    list_groups, get_group_members, delete_group,
)


@click.group("group")
def group_cmd():
    """Manage profile groups."""


@group_cmd.command("add")
@click.argument("group")
@click.argument("profile")
def group_add(group, profile):
    """Add PROFILE to GROUP."""
    try:
        add_to_group(group, profile)
        click.echo(f"Added '{profile}' to group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("remove")
@click.argument("group")
@click.argument("profile")
def group_remove(group, profile):
    """Remove PROFILE from GROUP."""
    try:
        remove_from_group(group, profile)
        click.echo(f"Removed '{profile}' from group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("list")
def group_list():
    """List all groups and their members."""
    groups = list_groups()
    if not groups:
        click.echo("No groups defined.")
        return
    for name, members in groups.items():
        click.echo(f"{name}: {', '.join(members)}")


@group_cmd.command("show")
@click.argument("group")
def group_show(group):
    """Show members of GROUP."""
    try:
        members = get_group_members(group)
        for m in members:
            click.echo(m)
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("delete")
@click.argument("group")
def group_delete(group):
    """Delete GROUP entirely."""
    try:
        delete_group(group)
        click.echo(f"Deleted group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
