"""CLI commands for profile notes."""

import click
from envswitch.note import set_note, get_note, remove_note, list_notes


@click.group("note")
def note_cmd():
    """Manage notes attached to profiles."""


@note_cmd.command("set")
@click.argument("profile")
@click.argument("text")
def note_set(profile, text):
    """Set a note for a profile."""
    try:
        set_note(profile, text)
        click.echo(f"Note set for profile '{profile}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@note_cmd.command("show")
@click.argument("profile")
def note_show(profile):
    """Show the note for a profile."""
    note = get_note(profile)
    if note is None:
        click.echo(f"No note for profile '{profile}'.")
    else:
        click.echo(note)


@note_cmd.command("remove")
@click.argument("profile")
def note_remove(profile):
    """Remove the note from a profile."""
    try:
        remove_note(profile)
        click.echo(f"Note removed from profile '{profile}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@note_cmd.command("list")
def note_list():
    """List all profiles with notes."""
    notes = list_notes()
    if not notes:
        click.echo("No notes found.")
        return
    for profile, text in notes.items():
        click.echo(f"{profile}: {text}")
