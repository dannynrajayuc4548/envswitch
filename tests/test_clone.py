"""Tests for envswitch.clone module."""

import pytest
from unittest.mock import patch

from envswitch.clone import clone_profile, ProfileNotFoundError, ProfileAlreadyExistsError


SAMPLE_PROFILES = {
    "dev": {"DB_HOST": "localhost", "DEBUG": "true", "PORT": "5432"},
    "prod": {"DB_HOST": "prod.db", "DEBUG": "false", "PORT": "5432"},
}


@pytest.fixture
def mock_storage():
    profiles = {k: dict(v) for k, v in SAMPLE_PROFILES.items()}
    with patch("envswitch.clone.load_profiles", return_value=profiles) as mock_load, \
         patch("envswitch.clone.save_profiles") as mock_save:
        yield mock_load, mock_save, profiles


def test_clone_profile_success(mock_storage):
    mock_load, mock_save, profiles = mock_storage
    result = clone_profile("dev", "dev-copy", {})
    assert result == {"DB_HOST": "localhost", "DEBUG": "true", "PORT": "5432"}
    assert mock_save.called


def test_clone_profile_with_overrides(mock_storage):
    mock_load, mock_save, profiles = mock_storage
    result = clone_profile("dev", "dev-staging", {"DB_HOST": "staging.db", "DEBUG": "false"})
    assert result["DB_HOST"] == "staging.db"
    assert result["DEBUG"] == "false"
    assert result["PORT"] == "5432"


def test_clone_profile_source_not_found(mock_storage):
    with pytest.raises(ProfileNotFoundError, match="'missing'"):
        clone_profile("missing", "new", {})


def test_clone_profile_destination_exists_no_overwrite(mock_storage):
    with pytest.raises(ProfileAlreadyExistsError, match="'prod'"):
        clone_profile("dev", "prod", {})


def test_clone_profile_destination_exists_with_overwrite(mock_storage):
    mock_load, mock_save, profiles = mock_storage
    result = clone_profile("dev", "prod", {"DEBUG": "true"}, overwrite=True)
    assert result["DEBUG"] == "true"
    assert result["DB_HOST"] == "localhost"
    assert mock_save.called


def test_clone_does_not_mutate_source(mock_storage):
    mock_load, mock_save, profiles = mock_storage
    clone_profile("dev", "dev-clone", {"PORT": "9999"})
    assert profiles["dev"]["PORT"] == "5432"
