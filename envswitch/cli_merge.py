"""CLI commands for profile merging."""

import click
from envswitch.merge import merge_profiles, ProfileNotFoundError, ProfileAlreadyExistsError


@click.command("merge")
@click.argument("sources", nargs=-1, required=True)
@click.option("-d", "--destination", required=True, help="Name of the merged profile.")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite destination profile if it already exists.",
)
def merge_cmd(sources: tuple, destination: str, overwrite: bool) -> None:
    """Merge two or more profiles into DESTINATION.

    Variables from later SOURCE profiles override earlier ones on conflict.

    Example:

      envswitch merge base staging -d staging-full
    """
    if len(sources) < 2:
        raise click.UsageError("At least two source profiles are required.")

    try:
        merged = merge_profiles(list(sources), destination, overwrite=overwrite)
    except ProfileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except ProfileAlreadyExistsError as exc:
        raise click.ClickException(str(exc)) from exc

    source_list = ", ".join(sources)
    click.echo(
        f"Merged {len(sources)} profiles ({source_list}) "
        f"into '{destination}' ({len(merged)} variables)."
    )
