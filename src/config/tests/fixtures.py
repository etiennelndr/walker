"""Internal Pytest fixtures."""

import pytest

from walker.config import Config


@pytest.fixture
def config() -> Config:
    return {
        "logging": {"level": "DEBUG", "destination": "config.log"},
        "null": None,
        "float": 4.2,
        "int": 29,
        "mapping": {"a": 5},
        "array": [1, "2", 3.0],
    }
