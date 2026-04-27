"""CLI commands for namespace management."""

import click

from envswitch.namespace import (
    NamespaceError,
    add_to_namespace,
    find_profile_namespaces,
    get_namespace_members,
    list_namespaces,
    remove_from_namespace,
)


@click.group("namespace", help="Organise profiles into named namespaces.")
def namespace_cmd() -> None:
    pass


@namespace_cmd.command("add")
@click.argument("namespace")
@click.argument("profile")
def ns_add(namespace: str, profile: str) -> None:
    """Add PROFILE to NAMESPACE."""
    try:
        add_to_namespace(namespace, profile)
        click.echo(f"Added '{profile}' to namespace '{namespace}'.")
    except NamespaceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@namespace_cmd.command("remove")
@click.argument("namespace")
@click.argument("profile")
def ns_remove(namespace: str, profile: str) -> None:
    """Remove PROFILE from NAMESPACE."""
    try:
        remove_from_namespace(namespace, profile)
        click.echo(f"Removed '{profile}' from namespace '{namespace}'.")
    except NamespaceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@namespace_cmd.command("list")
def ns_list() -> None:
    """List all namespaces."""
    namespaces = list_namespaces()
    if not namespaces:
        click.echo("No namespaces defined.")
        return
    for ns in namespaces:
        click.echo(ns)


@namespace_cmd.command("show")
@click.argument("namespace")
def ns_show(namespace: str) -> None:
    """Show profiles in NAMESPACE."""
    try:
        members = get_namespace_members(namespace)
    except NamespaceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if not members:
        click.echo(f"Namespace '{namespace}' is empty.")
        return
    for profile in members:
        click.echo(profile)


@namespace_cmd.command("find")
@click.argument("profile")
def ns_find(profile: str) -> None:
    """Find all namespaces containing PROFILE."""
    namespaces = find_profile_namespaces(profile)
    if not namespaces:
        click.echo(f"Profile '{profile}' is not in any namespace.")
        return
    for ns in namespaces:
        click.echo(ns)
