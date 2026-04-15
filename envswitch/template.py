"""Template rendering for environment variable profiles."""

import re
from typing import Dict, Optional


class TemplateError(Exception):
    """Raised when template rendering fails."""
    pass


def render_template(template: str, variables: Dict[str, str]) -> str:
    """Render a template string using profile variables.

    Supports {{VAR_NAME}} syntax for variable substitution.

    Args:
        template: Template string with {{VAR_NAME}} placeholders.
        variables: Dictionary of variable names to values.

    Returns:
        Rendered string with placeholders replaced.

    Raises:
        TemplateError: If a referenced variable is not found.
    """
    pattern = re.compile(r'\{\{\s*(\w+)\s*\}\}')
    missing = []

    def replace(match: re.Match) -> str:
        var_name = match.group(1)
        if var_name not in variables:
            missing.append(var_name)
            return match.group(0)
        return variables[var_name]

    result = pattern.sub(replace, template)

    if missing:
        raise TemplateError(
            f"Template references undefined variables: {', '.join(missing)}"
        )

    return result


def render_profile_values(
    profile_vars: Dict[str, str],
    context: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Render all values in a profile using the profile itself as context.

    Values can reference other variables in the same profile using
    {{VAR_NAME}} syntax. If extra context is provided, it takes precedence.

    Args:
        profile_vars: The profile's variable dictionary.
        context: Optional additional variables for rendering.

    Returns:
        New dictionary with all values rendered.

    Raises:
        TemplateError: If any value references an undefined variable.
    """
    merged_context = dict(profile_vars)
    if context:
        merged_context.update(context)

    rendered = {}
    for key, value in profile_vars.items():
        rendered[key] = render_template(value, merged_context)

    return rendered
