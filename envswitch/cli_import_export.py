"""CLI commands for importing and exporting profile files."""
import click

from envswitch.import_export_file import (
    export_to_file,
    import_from_file,
    ExportFileError,
    ImportError,
)


@click.group("file")
def file_cmd():
    """Import/export profiles from files."""


@file_cmd.command("export")
@click.argument("path")
@click.option("--profiles", "-p", multiple=True, help="Profile names to export (default: all)")
def file_export(path, profiles):
    """Export profiles to a JSON file."""
    try:
        exported = export_to_file(path, list(profiles) if profiles else None)
        click.echo(f"Exported {len(exported)} profile(s) to {path}")
    except ExportFileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@file_cmd.command("import")
@click.argument("path")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing profiles")
def file_import(path, overwrite):
    """Import profiles from a JSON file."""
    try:
        imported = import_from_file(path, overwrite=overwrite)
        if imported:
            click.echo(f"Imported {len(imported)} profile(s): {', '.join(imported)}")
        else:
            click.echo("No new profiles imported (use --overwrite to replace existing)")
    except ImportError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
