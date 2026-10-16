"""Internal Pytest fixtures."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
import pytest_asyncio
from quart import Blueprint, Quart

from tests.data import CONFIG_FOLDER
from walker.api.app import create_app
from walker.api.bp.states import states_bp
from walker.api.bp.walks import walks_bp


@pytest.fixture
def environment() -> str:
    return "test"


@pytest.fixture
def training_path(tmp_path: Path) -> Path:
    """Path of the file in which training states are stored."""
    return tmp_path / "training_states.jsonl"


@pytest.fixture
def environment_variables(
    environment: str,
    training_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sets environment variables required for testing."""
    monkeypatch.setenv("WALKERAPIDIR", str(CONFIG_FOLDER))
    monkeypatch.setenv("WALKER_API_ENV", environment)
    monkeypatch.setenv("WALKER_API_TRAINING__PATH", str(training_path))


@asynccontextmanager
async def serve_app(*blueprints: Blueprint) -> AsyncGenerator[Quart]:
    """Creates an application made of the given blueprints, and serves it."""
    app = create_app(blueprints)

    await app.startup()
    try:
        yield app
    finally:
        await app.shutdown()


@pytest_asyncio.fixture
async def app(environment_variables: None) -> AsyncGenerator[Quart]:
    """An application without any blueprint."""
    async with serve_app() as app:
        yield app


@pytest_asyncio.fixture
async def walks_app(environment_variables: None) -> AsyncGenerator[Quart]:
    """The application run by the `serve` command."""
    async with serve_app(walks_bp) as app:
        yield app


@pytest_asyncio.fixture
async def states_app(environment_variables: None) -> AsyncGenerator[Quart]:
    """The application run by the `collect` command."""
    async with serve_app(states_bp) as app:
        yield app
