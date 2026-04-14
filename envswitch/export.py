"""Export environment profiles to shell-compatible formats."""

from typing import Dict, Optional

SUPPORTED_SHELLS = ["bash", "zsh", "fish", "powershell"]


def export_bash(env_vars: Dict[str, str]) -> str:
    """Export environment variables as bash/zsh export statements."""
    lines = []
    for key, value in sorted(env_vars.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines)


def export_fish(env_vars: Dict[str, str]) -> str:
    """Export environment variables as fish shell set statements."""
    lines = []
    for key, value in sorted(env_vars.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'set -x {key} "{escaped}"')
    return "\n".join(lines)


def export_powershell(env_vars: Dict[str, str]) -> str:
    """Export environment variables as PowerShell statements."""
    lines = []
    for key, value in sorted(env_vars.items()):
        escaped = value.replace('"', '`"')
        lines.append(f'$env:{key} = "{escaped}"')
    return "\n".join(lines)


def export_dotenv(env_vars: Dict[str, str]) -> str:
    """Export environment variables as .env file format."""
    lines = []
    for key, value in sorted(env_vars.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines)


def export_profile(
    env_vars: Dict[str, str],
    shell: str = "bash",
    fmt: Optional[str] = None,
) -> str:
    """Export a profile's env vars to the specified shell format."""
    target = fmt or shell
    if target in ("bash", "zsh"):
        return export_bash(env_vars)
    elif target == "fish":
        return export_fish(env_vars)
    elif target == "powershell":
        return export_powershell(env_vars)
    elif target == "dotenv":
        return export_dotenv(env_vars)
    else:
        raise ValueError(
            f"Unsupported format: '{target}'. "
            f"Choose from: bash, zsh, fish, powershell, dotenv"
        )
