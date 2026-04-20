import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from envswitch import note as note_mod


SAMPLE_PROFILES = {"dev": {"KEY": "val"}, "prod": {"KEY": "prod_val"}}


@pytest.fixture
def notes_file(tmp_path, monkeypatch):
    notes_path = tmp_path / "notes.json"
    monkeypatch.setattr(note_mod, "get_notes_path", lambda: notes_path)
    monkeypatch.setattr(note_mod, "load_profiles", lambda: SAMPLE_PROFILES)
    return notes_path


def test_load_notes_missing_file(notes_file):
    assert note_mod.load_notes() == {}


def test_load_notes_invalid_json(notes_file):
    notes_file.write_text("not json")
    assert note_mod.load_notes() == {}


def test_load_notes_invalid_format(notes_file):
    notes_file.write_text("[1, 2, 3]")
    assert note_mod.load_notes() == {}


def test_set_and_get_note(notes_file):
    note_mod.set_note("dev", "This is dev")
    assert note_mod.get_note("dev") == "This is dev"


def test_set_note_profile_not_found(notes_file):
    with pytest.raises(KeyError):
        note_mod.set_note("missing", "text")


def test_get_note_missing(notes_file):
    assert note_mod.get_note("dev") is None


def test_remove_note(notes_file):
    note_mod.set_note("dev", "hello")
    note_mod.remove_note("dev")
    assert note_mod.get_note("dev") is None


def test_remove_note_not_found(notes_file):
    with pytest.raises(KeyError):
        note_mod.remove_note("dev")


def test_list_notes(notes_file):
    note_mod.set_note("dev", "note1")
    note_mod.set_note("prod", "note2")
    notes = note_mod.list_notes()
    assert notes == {"dev": "note1", "prod": "note2"}
