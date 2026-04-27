"""Namespace support: organize profiles under named namespaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envswitch.storage import load_profiles


class NamespaceError(Exception):
    pass


def get_namespaces_path() -> Path:
    from envswitch.storage import get_profiles_path

    return get_profiles_path().parent / "namespaces.json"


def load_namespaces() -> Dict[str, List[str]]:
    path = get_namespaces_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(v, list)}


def save_namespaces(namespaces: Dict[str, List[str]]) -> None:
    path = get_namespaces_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(namespaces, indent=2))


def add_to_namespace(namespace: str, profile: str) -> None:
    profiles = load_profiles()
    if profile not in profiles:
        raise NamespaceError(f"Profile '{profile}' not found.")
    namespaces = load_namespaces()
    members = namespaces.setdefault(namespace, [])
    if profile not in members:
        members.append(profile)
    save_namespaces(namespaces)


def remove_from_namespace(namespace: str, profile: str) -> None:
    namespaces = load_namespaces()
    if namespace not in namespaces:
        raise NamespaceError(f"Namespace '{namespace}' not found.")
    members = namespaces[namespace]
    if profile not in members:
        raise NamespaceError(f"Profile '{profile}' is not in namespace '{namespace}'.")
    members.remove(profile)
    if not members:
        del namespaces[namespace]
    save_namespaces(namespaces)


def list_namespaces() -> List[str]:
    return sorted(load_namespaces().keys())


def get_namespace_members(namespace: str) -> List[str]:
    namespaces = load_namespaces()
    if namespace not in namespaces:
        raise NamespaceError(f"Namespace '{namespace}' not found.")
    return list(namespaces[namespace])


def find_profile_namespaces(profile: str) -> List[str]:
    """Return all namespaces that contain the given profile."""
    namespaces = load_namespaces()
    return sorted(ns for ns, members in namespaces.items() if profile in members)
