"""CLI commands for viewing and managing profile switch history."""

from __future__ import annotations

import click

from .history import get_history, clear_history


@click.group("history")
def history_cmd() -> None:
    """View and manage profile switch history."""


@history_cmd.command("show")
@click.option(
    "--dir",
    "directory",
    default=None,
    help="Directory to show history for (defaults to current directory).",
)
def show_cmd(directory: str | None) -> None:
    """Show recent profile switches for a directory."""
    entries = get_history(cwd=directory)
    if not entries:
        click.echo("No history found for this directory.")
        return
    click.echo(f"{'PROFILE':<30} {'TIMESTAMP'}")
    click.echo("-" * 60)
    for entry in reversed(entries):
        click.echo(f"{entry['profile']:<30} {entry['timestamp']}")


@history_cmd.command("clear")
@click.option(
    "--dir",
    "directory",
    default=None,
    help="Directory to clear history for. Clears all history if omitted.",
)
@click.option("--all", "all_dirs", is_flag=True, default=False, help="Clear all history.")
@click.confirmation_option(prompt="Are you sure you want to clear history?")
def clear_cmd(directory: str | None, all_dirs: bool) -> None:
    """Clear profile switch history."""
    if all_dirs:
        clear_history(cwd=None)
        click.echo("All history cleared.")
    else:
        clear_history(cwd=directory)
        target = directory or "current directory"
        click.echo(f"History cleared for {target}.")
