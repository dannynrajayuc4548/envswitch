"""CLI commands for profile scheduling."""

import click
from envswitch.schedule import add_schedule, remove_schedule, get_schedule, load_schedules, get_active_profile


@click.group("schedule")
def schedule_cmd():
    """Manage time-based profile schedules."""


@schedule_cmd.command("add")
@click.argument("profile")
@click.option("--start", required=True, help="Start time in HH:MM format.")
@click.option("--end", required=True, help="End time in HH:MM format.")
@click.option("--days", default="", help="Comma-separated days (e.g. monday,tuesday). Leave empty for all days.")
def sched_add(profile, start, end, days):
    """Add a schedule for a profile."""
    day_list = [d.strip() for d in days.split(",") if d.strip()] if days else []
    try:
        add_schedule(profile, start, end, day_list)
        click.echo(f"Schedule added for profile '{profile}': {start} - {end}.")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@schedule_cmd.command("remove")
@click.argument("profile")
def sched_remove(profile):
    """Remove a schedule for a profile."""
    try:
        remove_schedule(profile)
        click.echo(f"Schedule removed for profile '{profile}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@schedule_cmd.command("list")
def sched_list():
    """List all schedules."""
    schedules = load_schedules()
    if not schedules:
        click.echo("No schedules defined.")
        return
    for profile, sched in schedules.items():
        days = ", ".join(sched["days"]) if sched["days"] else "every day"
        click.echo(f"{profile}: {sched['start']} - {sched['end']} ({days})")


@schedule_cmd.command("active")
def sched_active():
    """Show the currently active scheduled profile."""
    profile = get_active_profile()
    if profile:
        click.echo(f"Active profile: {profile}")
    else:
        click.echo("No profile is active at this time.")
