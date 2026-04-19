"""Lint profiles for common issues and best practices."""

from envswitch.storage import load_profiles


class LintWarning:
    def __init__(self, profile, key, message, level="warning"):
        self.profile = profile
        self.key = key
        self.message = message
        self.level = level

    def __repr__(self):
        return f"LintWarning({self.profile!r}, {self.key!r}, {self.message!r})"


def lint_profile(name, variables):
    warnings = []

    for key, value in variables.items():
        if key != key.upper():
            warnings.append(LintWarning(name, key, "Variable name is not uppercase", "style"))

        if not key or not key[0].isalpha() and key[0] != '_':
            warnings.append(LintWarning(name, key, "Variable name starts with invalid character", "error"))

        if value == "":
            warnings.append(LintWarning(name, key, "Variable has empty value", "warning"))

        if any(c in value for c in ['\n', '\r']):
            warnings.append(LintWarning(name, key, "Variable value contains newline characters", "warning"))

        if len(value) > 4096:
            warnings.append(LintWarning(name, key, "Variable value exceeds 4096 characters", "warning"))

    if not variables:
        warnings.append(LintWarning(name, None, "Profile has no variables defined", "info"))

    return warnings


def lint_all(profiles=None):
    if profiles is None:
        profiles = load_profiles()
    results = {}
    for name, variables in profiles.items():
        issues = lint_profile(name, variables)
        if issues:
            results[name] = issues
    return results
