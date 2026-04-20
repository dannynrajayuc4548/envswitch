"""CLI commands for the promote feature."""

import click
from envswitch.promote import ProfileNotFoundError, PromoteError, promote_profile


@click.group("promote")
def promote_cmd() -> None:
    """Promote variables from one profile into another."""


@promote_cmd.command("run")
@click.argument("source")
@click.argument("destination")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing keys in the destination profile.",
)
@click.option(
    "--key",
    "keys",
    multiple=True,
    metavar="KEY",
    help="Specific variable key(s) to promote. Can be repeated.",
)
def promote_run(
    source: str,
    destination: str,
    overwrite: bool,
    keys: tuple[str, ...],
) -> None:
    """Promote variables from SOURCE into DESTINATION profile.

    By default all variables are promoted. Use --key to select specific ones.
    """
    try:
        updated = promote_profile(
            source,
            destination,
            overwrite=overwrite,
            keys=list(keys) if keys else None,
        )
    except ProfileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except PromoteError as exc:
        raise click.ClickException(str(exc)) from exc

    promoted_keys = list(keys) if keys else "all"
    click.echo(
        f"Promoted {promoted_keys} from '{source}' into '{destination}'. "
        f"Destination now has {len(updated)} variable(s)."
    )
