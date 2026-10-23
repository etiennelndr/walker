"""Command-line interface entry point."""

import asyncio
import sys
from collections.abc import Sequence
from typing import Any

import click
from quart import Blueprint

from . import get_package_name, get_package_version
from .app import create_app
from .asgi import ASGIServerHandler, create_asgi_server, serve_asgi_server_handlers
from .bp.records import records_bp
from .bp.walks import walks_bp


def _serve(*blueprints: Blueprint) -> None:
    """Serves an application made of the given blueprints on an ASGI server."""
    asgi_server = create_asgi_server(create_app(blueprints))

    asyncio.run(
        serve_asgi_server_handlers(ASGIServerHandler(asgi_server)),
        loop_factory=asgi_server.config.get_loop_factory(),
    )


@click.group(name="walker-api")
@click.version_option(
    version=get_package_version(),
    package_name=get_package_name(),
)
def cli() -> None:
    """Main entry-point of the CLI."""


@cli.command(name="serve")
def serve() -> None:
    """Serves the generation of walker movements on an ASGI server."""
    _serve(walks_bp)


@cli.command(name="collect")
def collect() -> None:
    """Serves the collection of training records on an ASGI server."""
    _serve(records_bp)


def run(argv: Sequence[str] | None = None, **opts: Any) -> None:
    """Runs CLI."""
    if argv is None:
        # The first element (i.e. the executed module) must not be kept, as otherwise Click tries to
        # retrieve a command with the module name
        argv = sys.argv[1:]

    cli(args=argv, **opts)


__all__ = ["run"]
