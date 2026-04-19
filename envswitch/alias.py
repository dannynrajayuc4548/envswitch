"""Profile alias management for envswitch."""

import json
from pathlib import Path
from envswitch.storage import load_profiles


class AliasError(Exception):
    pass


def get_alias_path() -> Path:
    from envswitch.storage import get_profiles_path
    return get_profiles_path().parent / "aliases.json"


def load_aliases(path: Path | None = None) -> dict:
    p = path or get_alias_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def save_aliases(aliases: dict, path: Path | None = None) -> None:
    p = path or get_alias_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(aliases, indent=2))


def add_alias(alias: str, profile: str, path: Path | None = None) -> None:
    profiles = load_profiles()
    if profile not in profiles:
        raise AliasError(f"Profile '{profile}' not found.")
    aliases = load_aliases(path)
    if alias in aliases:
        raise AliasError(f"Alias '{alias}' already exists.")
    aliases[alias] = profile
    save_aliases(aliases, path)


def remove_alias(alias: str, path: Path | None = None) -> None:
    aliases = load_aliases(path)
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' not found.")
    del aliases[alias]
    save_aliases(aliases, path)


def resolve_alias(alias: str, path: Path | None = None) -> str | None:
    aliases = load_aliases(path)
    return aliases.get(alias)


def list_aliases(path: Path | None = None) -> dict:
    return load_aliases(path)
