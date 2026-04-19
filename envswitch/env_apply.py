"""Apply a profile's environment variables to a shell session script."""

from pathlib import Path
from typing import Optional
from envswitch.storage import load_profiles
from envswitch.lock_guard import abort_if_locked


class ProfileNotFoundError(Exception):
    pass


def apply_profile(profile_name: str, shell: str = "bash") -> str:
    """Return a shell script string that exports the profile's variables."""
    profiles = load_profiles()
    if profile_name not in profiles:
        raise ProfileNotFoundError(f"Profile '{profile_name}' not found.")

    abort_if_locked(profile_name)

    variables = profiles[profile_name]
    lines = []

    if shell == "bash":
        for key, value in variables.items():
            escaped = value.replace('"', '\\"')
            lines.append(f'export {key}="{escaped}"')
    elif shell == "fish":
        for key, value in variables.items():
            escaped = value.replace('"', '\\"')
            lines.append(f'set -x {key} "{escaped}"')
    elif shell == "powershell":
        for key, value in variables.items():
            escaped = value.replace('"', '`"')
            lines.append(f'$env:{key} = "{escaped}"')
    else:
        raise ValueError(f"Unsupported shell: {shell}")

    return "\n".join(lines)


def write_apply_script(profile_name: str, output_path: Path, shell: str = "bash") -> None:
    """Write the apply script to a file."""
    script = apply_profile(profile_name, shell)
    output_path.write_text(script)
