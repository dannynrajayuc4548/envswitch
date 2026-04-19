"""Tests for envswitch.lint module."""

import pytest
from unittest.mock import patch
from envswitch.lint import lint_profile, lint_all, LintWarning


def test_lint_uppercase_warning():
    warnings = lint_profile("dev", {"myvar": "value"})
    messages = [w.message for w in warnings]
    assert any("uppercase" in m for m in messages)


def test_lint_no_warning_for_uppercase():
    warnings = lint_profile("dev", {"MY_VAR": "value"})
    assert not any("uppercase" in w.message for w in warnings)


def test_lint_empty_value_warning():
    warnings = lint_profile("dev", {"MY_VAR": ""})
    messages = [w.message for w in warnings]
    assert any("empty" in m for m in messages)


def test_lint_newline_in_value():
    warnings = lint_profile("dev", {"MY_VAR": "hello\nworld"})
    messages = [w.message for w in warnings]
    assert any("newline" in m for m in messages)


def test_lint_empty_profile():
    warnings = lint_profile("dev", {})
    assert any(w.level == "info" for w in warnings)
    assert any("no variables" in w.message for w in warnings)


def test_lint_invalid_start_char():
    warnings = lint_profile("dev", {"1BAD": "val"})
    messages = [w.message for w in warnings]
    assert any("invalid character" in m for m in messages)


def test_lint_all_returns_only_profiles_with_issues():
    profiles = {
        "clean": {"MY_VAR": "value"},
        "dirty": {"lower": ""},
    }
    with patch("envswitch.lint.load_profiles", return_value=profiles):
        results = lint_all()
    assert "dirty" in results
    assert "clean" not in results


def test_lint_all_accepts_profiles_arg():
    profiles = {"p": {"X": "ok"}}
    results = lint_all(profiles=profiles)
    assert results == {}


def test_lint_warning_repr():
    w = LintWarning("dev", "KEY", "some message")
    assert "dev" in repr(w)
    assert "KEY" in repr(w)
