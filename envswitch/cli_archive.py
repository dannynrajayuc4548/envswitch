"""CLI commands for archiving and restoring profiles."""

import click

from envswitch.archive import ArchiveError, archive_profile, list_archived, restore_profile


@click.group("archive", help="Archive and restore deleted profiles.")
def archive_cmd() -> None:
    pass


@archive_cmd.command("add", help="Archive (remove) a profile, keeping a copy for later restore.")
@click.argument("name")
def arch_add(name: str) -> None:
    try:
        archive_profile(name)
        click.echo(f"Profile '{name}' archived successfully.")
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@archive_cmd.command("list", help="List archived profiles.")
@click.argument("name", required=False, default=None)
def arch_list(name: str | None) -> None:
    data = list_archived(name)
    if not data or all(len(v) == 0 for v in data.values()):
        click.echo("No archived profiles found.")
        return
    for profile_name, entries in data.items():
        for idx, entry in enumerate(entries):
            click.echo(
                f"[{idx}] {profile_name}  archived_at={entry.get('archived_at', 'unknown')}"
            )


@archive_cmd.command("restore", help="Restore an archived profile.")
@click.argument("name")
@click.option("--index", "-i", default=-1, show_default=True, help="Archive entry index (-1 = latest).")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite if profile already exists.")
def arch_restore(name: str, index: int, overwrite: bool) -> None:
    try:
        restore_profile(name, index=index, overwrite=overwrite)
        click.echo(f"Profile '{name}' restored successfully.")
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
