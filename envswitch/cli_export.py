"""CLI commands for exporting environment profiles."""

import click
from envswitch.storage import load_profiles
from envswitch.export import export_profile, SUPPORTED_SHELLS


@click.command("export")
@click.argument("profile_name")
@click.option(
    "--shell",
    "-s",
    default="bash",
    show_default=True,
    help="Target shell format.",
    type=click.Choice(["bash", "zsh", "fish", "powershell", "dotenv"], case_sensitive=False),
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Write output to a file instead of stdout.",
    type=click.Path(),
)
def export_cmd(profile_name: str, shell: str, output: str) -> None:
    """Export a profile's variables in shell-compatible format.

    Example usage:

      eval $(envswitch export myprofile --shell bash)
    """
    profiles = load_profiles()
    if profile_name not in profiles:
        raise click.ClickException(f"Profile '{profile_name}' not found.")

    env_vars = profiles[profile_name]
    if not env_vars:
        raise click.ClickException(f"Profile '{profile_name}' has no variables to export.")

    try:
        result = export_profile(env_vars, shell=shell.lower())
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if output:
        with open(output, "w") as fh:
            fh.write(result + "\n")
        click.echo(f"Exported profile '{profile_name}' to {output}")
    else:
        click.echo(result)
