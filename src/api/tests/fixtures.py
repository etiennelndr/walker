"""Internal Pytest fixtures."""

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from quart import Quart

from tests.app import serve_app
from tests.data import CONFIG_FOLDER
from walker.api.bp.records import records_bp
from walker.api.bp.walks import walks_bp


@pytest.fixture
def environment() -> str:
    return "test"


@pytest.fixture
def training_path(tmp_path: Path) -> Path:
    """Path of the file in which training records are stored."""
    return tmp_path / "training_records.jsonl"


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
async def records_app(environment_variables: None) -> AsyncGenerator[Quart]:
    """The application run by the `collect` command."""
    async with serve_app(records_bp) as app:
        yield app
