"""CLI commands for formatted profile display."""

import click
from envswitch.storage import load_profiles
from envswitch.fmt import format_profile, SUPPORTED_FORMATS


@click.group(name="fmt")
def fmt_cmd():
    """Format and display profiles in various output styles."""


@fmt_cmd.command(name="show")
@click.argument("profile")
@click.option(
    "--format", "-f",
    "fmt",
    default="table",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    help="Output format.",
)
def fmt_show(profile: str, fmt: str):
    """Display a profile in the chosen format."""
    profiles = load_profiles()
    if profile not in profiles:
        click.echo(f"Error: profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    click.echo(format_profile(profile, profiles[profile], fmt=fmt), nl=False)


@fmt_cmd.command(name="all")
@click.option(
    "--format", "-f",
    "fmt",
    default="table",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    help="Output format.",
)
def fmt_all(fmt: str):
    """Display all profiles in the chosen format."""
    profiles = load_profiles()
    if not profiles:
        click.echo("No profiles found.")
        return
    for name, variables in sorted(profiles.items()):
        click.echo(format_profile(name, variables, fmt=fmt), nl=False)
        click.echo()
