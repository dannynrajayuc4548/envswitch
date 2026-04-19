"""CLI commands for watching profile changes."""
import click
from envswitch.watch import ProfileWatcher, format_watch_diff
from envswitch.storage import load_profiles


@click.group(name="watch")
def watch_cmd():
    """Watch a profile for live changes."""


@watch_cmd.command(name="start")
@click.argument("profile")
@click.option("--interval", default=2.0, show_default=True, help="Poll interval in seconds.")
@click.option("--once", is_flag=True, help="Check once and exit instead of looping.")
def watch_start(profile: str, interval: float, once: bool):
    """Watch PROFILE for variable changes and print diffs."""
    profiles = load_profiles()
    if profile not in profiles:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)

    def on_change(old: dict, new: dict):
        click.echo(f"[envswitch] Profile '{profile}' changed:")
        click.echo(format_watch_diff(old, new))

    watcher = ProfileWatcher(profile, on_change, interval=interval)

    if once:
        changed = watcher.check_once()
        if not changed:
            click.echo(f"No changes detected in '{profile}'.")
        return

    click.echo(f"Watching profile '{profile}' every {interval}s. Press Ctrl+C to stop.")
    try:
        watcher.start()
    except KeyboardInterrupt:
        click.echo("\nStopped watching.")
