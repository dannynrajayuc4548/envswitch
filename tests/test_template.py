"""Tests for envswitch.template module."""

import pytest
from envswitch.template import render_template, render_profile_values, TemplateError


def test_render_template_simple_substitution():
    result = render_template("Hello, {{NAME}}!", {"NAME": "world"})
    assert result == "Hello, world!"


def test_render_template_multiple_vars():
    result = render_template(
        "{{PROTO}}://{{HOST}}:{{PORT}}",
        {"PROTO": "https", "HOST": "example.com", "PORT": "8080"},
    )
    assert result == "https://example.com:8080"


def test_render_template_no_placeholders():
    result = render_template("no placeholders here", {"FOO": "bar"})
    assert result == "no placeholders here"


def test_render_template_whitespace_in_placeholder():
    result = render_template("{{ NAME }}", {"NAME": "padded"})
    assert result == "padded"


def test_render_template_missing_variable_raises():
    with pytest.raises(TemplateError) as exc_info:
        render_template("Hello, {{MISSING}}!", {})
    assert "MISSING" in str(exc_info.value)


def test_render_template_multiple_missing_vars_raises():
    with pytest.raises(TemplateError) as exc_info:
        render_template("{{A}} and {{B}}", {})
    error_msg = str(exc_info.value)
    assert "A" in error_msg
    assert "B" in error_msg


def test_render_template_repeated_placeholder():
    result = render_template("{{X}}-{{X}}", {"X": "repeat"})
    assert result == "repeat-repeat"


def test_render_profile_values_self_referencing():
    profile = {
        "BASE_URL": "https://example.com",
        "API_URL": "{{BASE_URL}}/api/v1",
    }
    rendered = render_profile_values(profile)
    assert rendered["BASE_URL"] == "https://example.com"
    assert rendered["API_URL"] == "https://example.com/api/v1"


def test_render_profile_values_with_extra_context():
    profile = {"GREETING": "Hello, {{USER}}!"}
    rendered = render_profile_values(profile, context={"USER": "Alice"})
    assert rendered["GREETING"] == "Hello, Alice!"


def test_render_profile_values_context_overrides_profile():
    profile = {"ENV": "dev", "URL": "http://{{ENV}}.example.com"}
    rendered = render_profile_values(profile, context={"ENV": "prod"})
    assert rendered["URL"] == "http://prod.example.com"


def test_render_profile_values_missing_var_raises():
    profile = {"URL": "{{UNDEFINED_VAR}}/path"}
    with pytest.raises(TemplateError) as exc_info:
        render_profile_values(profile)
    assert "UNDEFINED_VAR" in str(exc_info.value)


def test_render_profile_values_no_templates():
    profile = {"FOO": "bar", "BAZ": "qux"}
    rendered = render_profile_values(profile)
    assert rendered == {"FOO": "bar", "BAZ": "qux"}
