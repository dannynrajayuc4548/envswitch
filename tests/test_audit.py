"""Tests for envswitch.audit module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envswitch import audit


@pytest.fixture
def audit_file(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.json"
    monkeypatch.setattr(audit, "get_audit_path", lambda: audit_path)
    return audit_path


def test_load_audit_missing_file(audit_file):
    assert audit.load_audit() == []


def test_load_audit_invalid_json(audit_file):
    audit_file.write_text("not json")
    assert audit.load_audit() == []


def test_load_audit_invalid_format(audit_file):
    audit_file.write_text(json.dumps({"bad": "format"}))
    assert audit.load_audit() == []


def test_save_and_load_audit(audit_file):
    entries = [{"action": "set", "profile": "prod", "timestamp": "2024-01-01T00:00:00+00:00"}]
    audit.save_audit(entries)
    assert audit.load_audit() == entries


def test_record_event_appends(audit_file):
    audit.record_event("set", "dev")
    audit.record_event("delete", "staging")
    entries = audit.load_audit()
    assert len(entries) == 2
    assert entries[0]["action"] == "set"
    assert entries[0]["profile"] == "dev"
    assert entries[1]["action"] == "delete"


def test_record_event_includes_timestamp(audit_file):
    audit.record_event("copy", "prod")
    entry = audit.load_audit()[0]
    assert "timestamp" in entry
    assert entry["timestamp"].endswith("+00:00")


def test_record_event_with_details(audit_file):
    audit.record_event("copy", "prod", details={"destination": "prod-backup"})
    entry = audit.load_audit()[0]
    assert entry["details"] == {"destination": "prod-backup"}


def test_get_audit_all(audit_file):
    audit.record_event("set", "dev")
    audit.record_event("set", "prod")
    result = audit.get_audit()
    assert len(result) == 2


def test_get_audit_filter_by_profile(audit_file):
    audit.record_event("set", "dev")
    audit.record_event("set", "prod")
    audit.record_event("delete", "dev")
    result = audit.get_audit(profile="dev")
    assert len(result) == 2
    assert all(e["profile"] == "dev" for e in result)


def test_get_audit_limit(audit_file):
    for i in range(10):
        audit.record_event("set", f"profile-{i}")
    result = audit.get_audit(limit=3)
    assert len(result) == 3
    assert result[-1]["profile"] == "profile-9"


def test_clear_audit(audit_file):
    audit.record_event("set", "dev")
    audit.clear_audit()
    assert audit.load_audit() == []
