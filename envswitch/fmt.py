"""Profile formatting/pretty-print module for envswitch."""

from typing import Optional


SUPPORTED_FORMATS = ("table", "json", "dotenv", "yaml")


def format_as_table(profile_name: str, variables: dict) -> str:
    """Render a profile as an ASCII table."""
    if not variables:
        return f"Profile '{profile_name}' has no variables.\n"

    key_width = max(len(k) for k in variables) + 2
    val_width = max(len(str(v)) for v in variables.values()) + 2
    key_width = max(key_width, 10)
    val_width = max(val_width, 10)

    sep = f"+{'-' * key_width}+{'-' * val_width}+"
    header = f"| {'KEY':<{key_width - 2}} | {'VALUE':<{val_width - 2}} |"
    lines = [f"Profile: {profile_name}", sep, header, sep]
    for k, v in sorted(variables.items()):
        lines.append(f"| {k:<{key_width - 2}} | {str(v):<{val_width - 2}} |")
    lines.append(sep)
    return "\n".join(lines) + "\n"


def format_as_json(profile_name: str, variables: dict) -> str:
    """Render a profile as pretty-printed JSON."""
    import json
    return json.dumps({profile_name: variables}, indent=2) + "\n"


def format_as_dotenv(profile_name: str, variables: dict) -> str:
    """Render a profile in .env file format."""
    lines = [f"# Profile: {profile_name}"]
    for k, v in sorted(variables.items()):
        escaped = str(v).replace('"', '\\"')
        lines.append(f'{k}="{escaped}"')
    return "\n".join(lines) + "\n"


def format_as_yaml(profile_name: str, variables: dict) -> str:
    """Render a profile as YAML."""
    lines = [f"{profile_name}:"]
    for k, v in sorted(variables.items()):
        escaped = str(v).replace('"', '\\"')
        lines.append(f'  {k}: "{escaped}"')
    return "\n".join(lines) + "\n"


def format_profile(
    profile_name: str,
    variables: dict,
    fmt: str = "table",
) -> str:
    """Dispatch to the requested formatter."""
    fmt = fmt.lower()
    if fmt == "table":
        return format_as_table(profile_name, variables)
    elif fmt == "json":
        return format_as_json(profile_name, variables)
    elif fmt == "dotenv":
        return format_as_dotenv(profile_name, variables)
    elif fmt == "yaml":
        return format_as_yaml(profile_name, variables)
    else:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}")
