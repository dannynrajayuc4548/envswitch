"""CLI commands for applying environment profiles."""

import click
from pathlib import Path
from envswitch.env_apply import apply_profile, write_apply_script, ProfileNotFoundError


@click.group(name="apply")
def apply_cmd():
    """Apply a profile to the current shell session."""


@apply_cmd.command(name="print")
@click.argument("profile")
@click.option("--shell", default="bash", type=click.Choice(["bash", "fish", "powershell"]), show_default=True)
def apply_print(profile, shell):
    """Print shell commands to export a profile's variables."""
    try:
        script = apply_profile(profile, shell)
        click.echo(script)
    except ProfileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@apply_cmd.command(name="write")
@click.argument("profile")
@click.argument("output", type=click.Path())
@click.option("--shell", default="bash", type=click.Choice(["bash", "fish", "powershell"]), show_default=True)
def apply_write(profile, output, shell):
    """Write shell export commands for a profile to a file."""
    try:
        write_apply_script(profile, Path(output), shell)
        click.echo(f"Script written to {output}")
    except ProfileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
