"""CLI commands for linting environment profiles."""

import click
from envswitch.lint import lint_all, lint_profile
from envswitch.storage import load_profiles


@click.group(name="lint")
def lint_cmd():
    """Lint profiles for issues and best practices."""


@lint_cmd.command(name="run")
@click.argument("profile", required=False)
@click.option("--level", type=click.Choice(["info", "style", "warning", "error"]), default=None, help="Filter by level.")
def lint_run(profile, level):
    """Run lint checks on one or all profiles."""
    profiles = load_profiles()

    if profile:
        if profile not in profiles:
            click.echo(f"Profile '{profile}' not found.", err=True)
            raise SystemExit(1)
        targets = {profile: profiles[profile]}
    else:
        targets = profiles

    if not targets:
        click.echo("No profiles found.")
        return

    found_any = False
    for name, variables in targets.items():
        issues = lint_profile(name, variables)
        if level:
            issues = [i for i in issues if i.level == level]
        if issues:
            found_any = True
            click.echo(f"\nProfile: {name}")
            for w in issues:
                key_part = f" [{w.key}]" if w.key else ""
                click.echo(f"  [{w.level.upper()}]{key_part} {w.message}")

    if not found_any:
        click.echo("No issues found.")
