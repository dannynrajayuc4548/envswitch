"""CLI commands for copying and renaming profiles."""

import click

from envswitch.copy import (
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    copy_profile,
    rename_profile,
)


@click.command("copy")
@click.argument("source")
@click.argument("destination")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite destination if it exists.")
def copy_cmd(source: str, destination: str, overwrite: bool) -> None:
    """Copy SOURCE profile to DESTINATION."""
    try:
        copy_profile(source, destination, overwrite=overwrite)
        click.echo(f"Profile '{source}' copied to '{destination}'.")
    except ProfileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except ProfileAlreadyExistsError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@click.command("rename")
@click.argument("source")
@click.argument("destination")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite destination if it exists.")
def rename_cmd(source: str, destination: str, overwrite: bool) -> None:
    """Rename SOURCE profile to DESTINATION."""
    try:
        rename_profile(source, destination, overwrite=overwrite)
        click.echo(f"Profile '{source}' renamed to '{destination}'.")
    except ProfileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except ProfileAlreadyExistsError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
