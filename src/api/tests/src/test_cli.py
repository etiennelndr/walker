from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from quart import Blueprint

from walker.api import cli, get_package_version
from walker.api.bp.records import records_bp
from walker.api.bp.walks import walks_bp


def test_version() -> None:
    result = CliRunner().invoke(cli.cli, ["--version"])

    assert result.exit_code == 0
    assert result.output == f"walker-api, version {get_package_version()}\n"


def test_help() -> None:
    result = CliRunner().invoke(cli.cli, ["--help"])

    assert result.exit_code == 0
    assert result.output.startswith("Usage: walker-api [OPTIONS] COMMAND [ARGS]...")
    assert "--version  Show the version and exit." in result.output
    assert "--help     Show this message and exit." in result.output


@pytest.mark.parametrize(
    ("command", "command_help"),
    [
        pytest.param(
            "serve",
            "Serves the generation of walker movements on an ASGI server.",
        ),
        pytest.param(
            "collect",
            "Serves the collection of training records on an ASGI server.",
        ),
    ],
)
def test_command_help(command: str, command_help: str) -> None:
    result = CliRunner().invoke(cli.cli, [command, "--help"])

    assert result.exit_code == 0
    assert result.output.startswith(f"Usage: walker-api {command} [OPTIONS]")
    assert command_help in result.output
    assert "--help  Show this message and exit." in result.output


@pytest.mark.parametrize(
    ("command", "blueprint"),
    [
        pytest.param("serve", walks_bp),
        pytest.param("collect", records_bp),
    ],
)
def test_command(monkeypatch: pytest.MonkeyPatch, command: str, blueprint: Blueprint) -> None:
    serve = Mock()
    monkeypatch.setattr(cli, "_serve", serve)

    result = CliRunner().invoke(cli.cli, [command])

    assert result.exit_code == 0
    serve.assert_called_once_with(blueprint)
