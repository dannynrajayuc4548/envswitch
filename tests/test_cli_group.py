import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from envswitch.cli_group import group_cmd
from envswitch.group import GroupError


@pytest.fixture
def runner():
    return CliRunner()


SAMPLE_GROUPS = {"backend": ["dev", "prod"], "infra": ["staging"]}


def test_group_add_success(runner):
    with patch("envswitch.cli_group.add_to_group") as m:
        result = runner.invoke(group_cmd, ["add", "backend", "dev"])
    assert result.exit_code == 0
    assert "Added" in result.output
    m.assert_called_once_with("backend", "dev")


def test_group_add_error(runner):
    with patch("envswitch.cli_group.add_to_group", side_effect=GroupError("Profile 'x' not found.")):
        result = runner.invoke(group_cmd, ["add", "backend", "x"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_group_remove_success(runner):
    with patch("envswitch.cli_group.remove_from_group") as m:
        result = runner.invoke(group_cmd, ["remove", "backend", "dev"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_group_remove_error(runner):
    with patch("envswitch.cli_group.remove_from_group", side_effect=GroupError("not found")):
        result = runner.invoke(group_cmd, ["remove", "x", "y"])
    assert result.exit_code == 1


def test_group_list_empty(runner):
    with patch("envswitch.cli_group.list_groups", return_value={}):
        result = runner.invoke(group_cmd, ["list"])
    assert "No groups" in result.output


def test_group_list_with_groups(runner):
    with patch("envswitch.cli_group.list_groups", return_value=SAMPLE_GROUPS):
        result = runner.invoke(group_cmd, ["list"])
    assert "backend" in result.output
    assert "dev" in result.output


def test_group_show_success(runner):
    with patch("envswitch.cli_group.get_group_members", return_value=["dev", "prod"]):
        result = runner.invoke(group_cmd, ["show", "backend"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_group_show_not_found(runner):
    with patch("envswitch.cli_group.get_group_members", side_effect=GroupError("not found")):
        result = runner.invoke(group_cmd, ["show", "ghost"])
    assert result.exit_code == 1


def test_group_delete_success(runner):
    with patch("envswitch.cli_group.delete_group") as m:
        result = runner.invoke(group_cmd, ["delete", "backend"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_group_delete_not_found(runner):
    with patch("envswitch.cli_group.delete_group", side_effect=GroupError("not found")):
        result = runner.invoke(group_cmd, ["delete", "ghost"])
    assert result.exit_code == 1
