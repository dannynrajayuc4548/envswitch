import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envswitch.import_export_file import (
    export_to_file,
    import_from_file,
    ExportFileError,
    ImportError,
)

SAMPLE = {"dev": {"DB": "dev_db"}, "prod": {"DB": "prod_db"}}


@pytest.fixture
def tmp_json(tmp_path):
    return str(tmp_path / "profiles.json")


def test_export_all_profiles(tmp_json):
    with patch("envswitch.import_export_file.load_profiles", return_value=SAMPLE):
        result = export_to_file(tmp_json)
    assert result == SAMPLE
    data = json.loads(Path(tmp_json).read_text())
    assert data["envswitch_profiles"] == SAMPLE


def test_export_selected_profiles(tmp_json):
    with patch("envswitch.import_export_file.load_profiles", return_value=SAMPLE):
        result = export_to_file(tmp_json, ["dev"])
    assert list(result.keys()) == ["dev"]


def test_export_missing_profile_raises(tmp_json):
    with patch("envswitch.import_export_file.load_profiles", return_value=SAMPLE):
        with pytest.raises(ExportFileError, match="staging"):
            export_to_file(tmp_json, ["staging"])


def test_import_success(tmp_json):
    Path(tmp_json).write_text(json.dumps({"envswitch_profiles": {"staging": {"X": "1"}}}))
    with patch("envswitch.import_export_file.load_profiles", return_value={}) as ml, \
         patch("envswitch.import_export_file.save_profiles") as ms:
        result = import_from_file(tmp_json)
    assert result == ["staging"]


def test_import_skips_existing_without_overwrite(tmp_json):
    Path(tmp_json).write_text(json.dumps({"envswitch_profiles": {"dev": {"X": "1"}}}))
    with patch("envswitch.import_export_file.load_profiles", return_value=SAMPLE), \
         patch("envswitch.import_export_file.save_profiles"):
        result = import_from_file(tmp_json, overwrite=False)
    assert result == []


def test_import_overwrite(tmp_json):
    Path(tmp_json).write_text(json.dumps({"envswitch_profiles": {"dev": {"X": "new"}}}))
    with patch("envswitch.import_export_file.load_profiles", return_value=SAMPLE), \
         patch("envswitch.import_export_file.save_profiles"):
        result = import_from_file(tmp_json, overwrite=True)
    assert "dev" in result


def test_import_file_not_found():
    with pytest.raises(ImportError, match="not found"):
        import_from_file("/nonexistent/path.json")


def test_import_invalid_json(tmp_json):
    Path(tmp_json).write_text("not json")
    with pytest.raises(ImportError, match="Invalid JSON"):
        import_from_file(tmp_json)


def test_import_missing_key(tmp_json):
    Path(tmp_json).write_text(json.dumps({"wrong_key": {}}))
    with pytest.raises(ImportError, match="envswitch_profiles"):
        import_from_file(tmp_json)
