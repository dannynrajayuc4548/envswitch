import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_note import note_cmd


@pytest.fixture
def runner():
    return CliRunner()


SAMPLE_PROFILES = {"dev": {"K": "v"}, "prod": {"K": "p"}}


def test_note_set_success(runner):
    with patch("envswitch.cli_note.set_note") as mock_set:
        result = runner.invoke(note_cmd, ["set", "dev", "my note"])
        mock_set.assert_called_once_with("dev", "my note")
        assert "Note set" in result.output


def test_note_set_profile_not_found(runner):
    with patch("envswitch.cli_note.set_note", side_effect=KeyError("Profile 'x' not found.")):
        result = runner.invoke(note_cmd, ["set", "x", "text"])
        assert result.exit_code == 1


def test_note_show_existing(runner):
    with patch("envswitch.cli_note.get_note", return_value="hello world"):
        result = runner.invoke(note_cmd, ["show", "dev"])
        assert "hello world" in result.output


def test_note_show_missing(runner):
    with patch("envswitch.cli_note.get_note", return_value=None):
        result = runner.invoke(note_cmd, ["show", "dev"])
        assert "No note" in result.output


def test_note_remove_success(runner):
    with patch("envswitch.cli_note.remove_note") as mock_rm:
        result = runner.invoke(note_cmd, ["remove", "dev"])
        mock_rm.assert_called_once_with("dev")
        assert "removed" in result.output


def test_note_remove_not_found(runner):
    with patch("envswitch.cli_note.remove_note", side_effect=KeyError("No note")):
        result = runner.invoke(note_cmd, ["remove", "dev"])
        assert result.exit_code == 1


def test_note_list_empty(runner):
    with patch("envswitch.cli_note.list_notes", return_value={}):
        result = runner.invoke(note_cmd, ["list"])
        assert "No notes" in result.output


def test_note_list_with_entries(runner):
    with patch("envswitch.cli_note.list_notes", return_value={"dev": "note1", "prod": "note2"}):
        result = runner.invoke(note_cmd, ["list"])
        assert "dev: note1" in result.output
        assert "prod: note2" in result.output
