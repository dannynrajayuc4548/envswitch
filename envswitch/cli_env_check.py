"""CLI commands for checking which profiles match the current environment."""

import click

from envswitch.env_check import check_profiles


@click.group(name="check")
def check_cmd():
    """Check which profiles match the current environment."""


@check_cmd.command(name="run")
@click.option(
    "--threshold",
    "-t",
    default=0.5,
    show_default=True,
    type=float,
    help="Minimum match ratio (0.0–1.0) to include a profile.",
)
@click.option(
    "--exact",
    is_flag=True,
    default=False,
    help="Only show profiles that match all variables exactly.",
)
def check_run(threshold: float, exact: bool):
    """Show profiles that match the current environment variables."""
    effective_threshold = 1.0 if exact else threshold
    results = check_profiles(threshold=effective_threshold)

    if not results:
        click.echo("No profiles match the current environment.")
        return

    label = "Exact matches" if exact else f"Profiles matching >= {effective_threshold:.0%}"
    click.echo(f"{label}:")
    click.echo()

    for r in results:
        marker = "✓" if r["exact"] else "~"
        click.echo(
            f"  {marker} {r['name']}  "
            f"{r['matching']}/{r['total']} vars  "
            f"({r['ratio']:.0%})"
        )
