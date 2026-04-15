import click
from .diff import diff_profiles, format_diff, ProfileNotFoundError
from .storage import load_profiles


@click.command(name="diff")
@click.argument("profile1")
@click.argument("profile2")
@click.option(
    "--no-color",
    is_flag=True,
    default=False,
    help="Disable colored output.",
)
def diff_cmd(profile1: str, profile2: str, no_color: bool) -> None:
    """Show differences between two environment profiles.

    Compares PROFILE1 and PROFILE2, displaying added, removed,
    and changed environment variables.
    """
    profiles = load_profiles()

    try:
        diff = diff_profiles(profiles, profile1, profile2)
    except ProfileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if not diff:
        click.echo(f"Profiles '{profile1}' and '{profile2}' are identical.")
        return

    lines = format_diff(diff)

    for line in lines:
        if no_color:
            click.echo(line)
        elif line.startswith("+"):
            click.echo(click.style(line, fg="green"))
        elif line.startswith("-"):
            click.echo(click.style(line, fg="red"))
        elif line.startswith("~"):
            click.echo(click.style(line, fg="yellow"))
        else:
            click.echo(line)
