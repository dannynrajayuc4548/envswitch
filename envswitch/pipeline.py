"""Pipeline: chain multiple profiles together, merging vars in order."""

from __future__ import annotations

from typing import Dict, List

from envswitch.storage import load_profiles


class PipelineError(Exception):
    pass


class ProfileNotFoundError(PipelineError):
    pass


def run_pipeline(profile_names: List[str]) -> Dict[str, str]:
    """Merge profiles left-to-right; later profiles override earlier ones."""
    if not profile_names:
        raise PipelineError("Pipeline requires at least one profile name.")

    profiles = load_profiles()
    result: Dict[str, str] = {}

    for name in profile_names:
        if name not in profiles:
            raise ProfileNotFoundError(f"Profile '{name}' not found.")
        result.update(profiles[name])

    return result


def describe_pipeline(profile_names: List[str]) -> List[Dict]:
    """Return a per-step breakdown showing which vars each profile contributes."""
    if not profile_names:
        raise PipelineError("Pipeline requires at least one profile name.")

    profiles = load_profiles()
    seen: Dict[str, str] = {}
    steps = []

    for name in profile_names:
        if name not in profiles:
            raise ProfileNotFoundError(f"Profile '{name}' not found.")
        profile = profiles[name]
        added = {k: v for k, v in profile.items() if k not in seen}
        overridden = {k: (seen[k], v) for k, v in profile.items() if k in seen and seen[k] != v}
        seen.update(profile)
        steps.append({"profile": name, "added": added, "overridden": overridden})

    return steps
