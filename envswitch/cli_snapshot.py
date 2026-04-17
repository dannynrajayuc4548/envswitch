"""CLI commands for profile snapshots."""
import click
from envswitch.snapshot import create_snapshot, list_snapshots, restore_snapshot, delete_snapshot
from envswitch.storage import load_profiles, save_profiles


@click.group("snapshot")
def snapshot_cmd():
    """Manage profile snapshots."""


@snapshot_cmd.command("create")
@click.argument("profile")
@click.option("--label", "-l", default=None, help="Optional label for the snapshot.")
def snap_create(profile, label):
    """Create a snapshot of PROFILE."""
    try:
        snap_id = create_snapshot(profile, label)
        click.echo(f"Snapshot created: {snap_id}")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@snapshot_cmd.command("list")
@click.argument("profile", required=False, default=None)
def snap_list(profile):
    """List snapshots, optionally filtered by PROFILE."""
    snaps = list_snapshots(profile)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        label = f" ({s['label']})" if s.get("label") else ""
        click.echo(f"{s['id']}{label}  [{len(s['vars'])} vars]")


@snapshot_cmd.command("restore")
@click.argument("snap_id")
def snap_restore(snap_id):
    """Restore a snapshot back into its profile."""
    try:
        vars_ = restore_snapshot(snap_id)
        profile_name = snap_id.split(":")[0]
        profiles = load_profiles()
        profiles[profile_name] = vars_
        save_profiles(profiles)
        click.echo(f"Profile '{profile_name}' restored from snapshot '{snap_id}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@snapshot_cmd.command("delete")
@click.argument("snap_id")
def snap_delete(snap_id):
    """Delete a snapshot."""
    try:
        delete_snapshot(snap_id)
        click.echo(f"Snapshot '{snap_id}' deleted.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
