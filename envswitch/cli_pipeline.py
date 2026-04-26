"""CLI commands for the pipeline feature."""

from __future__ import annotations

import click

from envswitch.pipeline import PipelineError, ProfileNotFoundError, describe_pipeline, run_pipeline


@click.group("pipeline", help="Chain profiles together into a merged variable set.")
def pipeline_cmd() -> None:
    pass


@pipeline_cmd.command("run")
@click.argument("profiles", nargs=-1, required=True)
@click.option("--format", "fmt", type=click.Choice(["dotenv", "json"]), default="dotenv", show_default=True)
def pipeline_run(profiles: tuple, fmt: str) -> None:
    """Merge PROFILES left-to-right and print the result."""
    try:
        result = run_pipeline(list(profiles))
    except ProfileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except PipelineError as exc:
        raise click.ClickException(str(exc))

    if fmt == "json":
        import json
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    else:
        for k, v in result.items():
            click.echo(f"{k}={v}")


@pipeline_cmd.command("describe")
@click.argument("profiles", nargs=-1, required=True)
def pipeline_describe(profiles: tuple) -> None:
    """Show a step-by-step breakdown of how PROFILES are merged."""
    try:
        steps = describe_pipeline(list(profiles))
    except ProfileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except PipelineError as exc:
        raise click.ClickException(str(exc))

    for step in steps:
        click.echo(f"\n[{step['profile']}]")
        for k, v in step["added"].items():
            click.echo(f"  + {k}={v}")
        for k, (old, new) in step["overridden"].items():
            click.echo(f"  ~ {k}: {old!r} -> {new!r}")
        if not step["added"] and not step["overridden"]:
            click.echo("  (no changes)")
