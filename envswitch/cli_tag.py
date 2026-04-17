"""CLI commands for profile tagging."""
import click
from envswitch.tag import add_tag, remove_tag, get_tags, find_by_tag


@click.group("tag")
def tag_cmd():
    """Manage profile tags."""


@tag_cmd.command("add")
@click.argument("profile")
@click.argument("tag")
def tag_add(profile, tag):
    """Add a tag to a profile."""
    try:
        add_tag(profile, tag)
        click.echo(f"Tagged '{profile}' with '{tag}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@tag_cmd.command("remove")
@click.argument("profile")
@click.argument("tag")
def tag_remove(profile, tag):
    """Remove a tag from a profile."""
    remove_tag(profile, tag)
    click.echo(f"Removed tag '{tag}' from '{profile}'.")


@tag_cmd.command("list")
@click.argument("profile")
def tag_list(profile):
    """List tags for a profile."""
    tags = get_tags(profile)
    if not tags:
        click.echo(f"No tags for '{profile}'.")
    else:
        for t in tags:
            click.echo(t)


@tag_cmd.command("find")
@click.argument("tag")
def tag_find(tag):
    """Find profiles with a given tag."""
    profiles = find_by_tag(tag)
    if not profiles:
        click.echo(f"No profiles tagged '{tag}'.")
    else:
        for p in profiles:
            click.echo(p)
