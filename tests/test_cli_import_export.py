import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envswitch.cli_import_export import file_cmd


@pytest.fixture
def runner():
    return CliRunner()


SAMPLE = {"dev": {"DB": "dev_db"}, "prod": {"DB": "prod_db"}}


def test_export_all(runner, tmp_path):
    out = str(tmp_path / "out.json")
    with patch("envswitch.import_export_file.load_profiles", return_value=SAMPLE):
        result = runner.invoke(file_cmd, ["export", out])
    assert result.exit_code == 0
    assert "2 profile(s)" in result.output


def test_export_selected(runner, tmp_path):
    out = str(tmp_path / "out.json")
    with patch("envswitch.import_export_file.load_profiles", return_value=SAMPLE):
        result = runner.invoke(file_cmd, ["export", out, "-p", "dev"])
    assert result.exit_code == 0
    assert "1 profile(s)" in result.output


def test_export_missing_profile(runner, tmp_path):
    out = str(tmp_path / "out.json")
    with patch("envswitch.import_export_file.load_profiles", return_value=SAMPLE):
        result = runner.invoke(file_cmd, ["export", out, "-p", "staging"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_import_success(runner, tmp_path):
    f = tmp_path / "in.json"
    f.write_text(json.dumps({"envswitch_profiles": {"staging": {"X": "1"}}}))
    with patch("envswitch.import_export_file.load_profiles", return_value={}), \
         patch("envswitch.import_export_file.save_profiles"):
        result = runner.invoke(file_cmd, ["import", str(f)])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_import_no_new_profiles(runner, tmp_path):
    f = tmp_path / "in.json"
    f.write_text(json.dumps({"envswitch_profiles": {"dev": {"DB": "x"}}}))
    with patch("envswitch.import_export_file.load_profiles", return_value=SAMPLE), \
         patch("envswitch.import_export_file.save_profiles"):
        result = runner.invoke(file_cmd, ["import", str(f)])
    assert "No new profiles" in result.output


def test_import_file_not_found(runner):
    result = runner.invoke(file_cmd, ["import", "/no/such/file.json"])
    assert result.exit_code == 1
    assert "Error" in result.output
