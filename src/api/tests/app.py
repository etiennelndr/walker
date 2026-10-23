"""Helpers to serve the application in tests."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from quart import Blueprint, Quart

from walker.api.app import create_app


@asynccontextmanager
async def serve_app(*blueprints: Blueprint) -> AsyncGenerator[Quart]:
    """Creates an application made of the given blueprints, and serves it.

    The application is shut down when leaving the context.
    """
    app = create_app(blueprints)

    await app.startup()
    try:
        yield app
    finally:
        await app.shutdown()


__all__ = ["serve_app"]
