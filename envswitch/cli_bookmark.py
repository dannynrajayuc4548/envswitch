"""CLI commands for managing profile bookmarks."""

import click

from envswitch.bookmark import (
    BookmarkError,
    add_bookmark,
    get_bookmark,
    list_bookmarks,
    remove_bookmark,
)


@click.group("bookmark")
def bookmark_cmd():
    """Manage named bookmarks for profiles."""


@bookmark_cmd.command("add")
@click.argument("name")
@click.argument("profile")
@click.option("--description", "-d", default="", help="Optional description for the bookmark.")
@click.option("--force", is_flag=True, help="Overwrite existing bookmark.")
def bookmark_add(name: str, profile: str, description: str, force: bool):
    """Add a bookmark NAME pointing to PROFILE."""
    from envswitch.bookmark import load_bookmarks, save_bookmarks

    if force:
        from envswitch.storage import load_profiles
        profiles = load_profiles()
        if profile not in profiles:
            click.echo(f"Error: Profile '{profile}' does not exist.", err=True)
            raise SystemExit(1)
        bookmarks = load_bookmarks()
        bookmarks[name] = {"profile": profile, "description": description}
        save_bookmarks(bookmarks)
        click.echo(f"Bookmark '{name}' -> '{profile}' saved.")
        return
    try:
        add_bookmark(name, profile, description)
        click.echo(f"Bookmark '{name}' -> '{profile}' saved.")
    except BookmarkError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@bookmark_cmd.command("remove")
@click.argument("name")
def bookmark_remove(name: str):
    """Remove a bookmark by NAME."""
    try:
        remove_bookmark(name)
        click.echo(f"Bookmark '{name}' removed.")
    except BookmarkError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@bookmark_cmd.command("show")
@click.argument("name")
def bookmark_show(name: str):
    """Show the profile a bookmark points to."""
    try:
        bm = get_bookmark(name)
        click.echo(f"Bookmark : {name}")
        click.echo(f"Profile  : {bm['profile']}")
        if bm.get("description"):
            click.echo(f"Desc     : {bm['description']}")
    except BookmarkError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@bookmark_cmd.command("list")
def bookmark_list():
    """List all bookmarks."""
    items = list_bookmarks()
    if not items:
        click.echo("No bookmarks defined.")
        return
    for bm in items:
        desc = f"  # {bm['description']}" if bm["description"] else ""
        click.echo(f"{bm['name']} -> {bm['profile']}{desc}")
