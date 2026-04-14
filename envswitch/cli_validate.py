"""CLI commands for validating environment variable profiles."""

import click
from envswitch.storage import load_profiles
from envswitch.validate import validate_profile


@click.command("validate")
@click.argument("profile", required=False)
def validate_cmd(profile: str | None):
    """Validate one or all profiles for correctness.

    If PROFILE is given, validate only that profile.
    Otherwise, validate all profiles.
    """
    profiles = load_profiles()

    if not profiles:
        click.echo("No profiles found.")
        return

    names_to_check = [profile] if profile else list(profiles.keys())
    missing = [n for n in names_to_check if n not in profiles]

    if missing:
        for name in missing:
            click.echo(click.style(f"Profile {name!r} not found.", fg="red"), err=True)
        raise SystemExit(1)

    all_valid = True
    for name in names_to_check:
        errors = validate_profile(name, profiles[name])
        if errors:
            all_valid = False
            click.echo(click.style(f"[INVALID] {name}", fg="red"))
            for error in errors:
                click.echo(f"  - {error}")
        else:
            click.echo(click.style(f"[OK]      {name}", fg="green"))

    if not all_valid:
        raise SystemExit(1)
