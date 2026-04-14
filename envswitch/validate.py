"""Validation utilities for environment variable profiles."""

import re
from typing import Dict, List, Tuple

# POSIX-compliant env var name pattern
ENV_VAR_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


class ValidationError(Exception):
    """Raised when profile validation fails."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation failed with {len(errors)} error(s): {'; '.join(errors)}")


def validate_var_name(name: str) -> bool:
    """Return True if name is a valid environment variable name."""
    return bool(ENV_VAR_PATTERN.match(name))


def validate_var_value(value: str) -> bool:
    """Return True if value is a string (all string values are valid)."""
    return isinstance(value, str)


def validate_profile_name(name: str) -> bool:
    """Return True if profile name is non-empty and contains no whitespace."""
    return bool(name) and not any(c.isspace() for c in name)


def validate_profile(name: str, variables: Dict[str, str]) -> List[str]:
    """Validate a profile name and its variables.

    Returns a list of error messages (empty list means valid).
    """
    errors: List[str] = []

    if not validate_profile_name(name):
        errors.append(f"Invalid profile name: {name!r} (must be non-empty and contain no whitespace)")

    if not isinstance(variables, dict):
        errors.append("Profile variables must be a dictionary")
        return errors

    for var_name, var_value in variables.items():
        if not validate_var_name(var_name):
            errors.append(
                f"Invalid variable name: {var_name!r} (must match [A-Za-z_][A-Za-z0-9_]*)"
            )
        if not validate_var_value(var_value):
            errors.append(
                f"Invalid value for {var_name!r}: must be a string, got {type(var_value).__name__}"
            )

    return errors


def validate_and_raise(name: str, variables: Dict[str, str]) -> None:
    """Validate a profile and raise ValidationError if invalid."""
    errors = validate_profile(name, variables)
    if errors:
        raise ValidationError(errors)
