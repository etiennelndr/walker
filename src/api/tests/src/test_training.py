import asyncio
import json
from pathlib import Path

import pytest

from tests.data import STATE
from walker.api.training import TrainingStore
from walker.core.resources.state import State


async def test_add(training_path: Path) -> None:
    states = [STATE, STATE | {"speed": {"x": 0.0, "y": 0.0, "z": 0.0}}]

    training_store = TrainingStore(training_path)
    await training_store.open()
    for state in states:
        training_store.add(State.decode(state))

    await training_store.close()

    stored_states = [json.loads(line) for line in training_path.read_text().splitlines()]
    assert stored_states == states


async def test_add_appends_to_existing_states(training_path: Path) -> None:
    for _ in range(2):
        training_store = TrainingStore(training_path)
        await training_store.open()
        training_store.add(State.decode(STATE))
        await training_store.close()

    stored_states = [json.loads(line) for line in training_path.read_text().splitlines()]
    assert stored_states == [STATE, STATE]


async def test_add_after_close(training_path: Path) -> None:
    training_store = TrainingStore(training_path)
    await training_store.open()
    await training_store.close()

    with pytest.raises(asyncio.QueueShutDown):
        training_store.add(State.decode(STATE))


async def test_close_twice(training_path: Path) -> None:
    training_store = TrainingStore(training_path)
    await training_store.open()

    await training_store.close()
    await training_store.close()
