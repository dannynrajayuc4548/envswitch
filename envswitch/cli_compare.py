"""CLI commands for comparing profiles."""
import click
from envswitch.compare import compare_profiles, format_compare, ProfileNotFoundError


@click.group(name="compare")
def compare_cmd():
    """Compare multiple profiles side by side."""
    pass


@compare_cmd.command(name="show")
@click.argument("profiles", nargs=-1, required=True)
@click.option("--raw", is_flag=True, help="Output raw key=value pairs per profile.")
def compare_show(profiles, raw):
    """Show a side-by-side comparison of two or more profiles."""
    if len(profiles) < 2:
        click.echo("Error: at least two profiles are required.", err=True)
        raise SystemExit(1)

    try:
        comparison = compare_profiles(list(profiles))
    except ProfileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    if not comparison:
        click.echo("No variables to compare.")
        return

    if raw:
        for key, values in comparison.items():
            for name in profiles:
                val = values[name]
                if val is not None:
                    click.echo(f"{name}: {key}={val}")
    else:
        click.echo(format_compare(comparison, list(profiles)))
