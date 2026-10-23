import asyncio
import json
from pathlib import Path

import pytest

from tests.data import TRAINING_RECORD
from walker.api.training import TrainingStore
from walker.core.resources.record import Record


async def test_add(training_path: Path) -> None:
    records = [TRAINING_RECORD, TRAINING_RECORD | {"frame": 43, "time": 4.3}]

    training_store = TrainingStore(training_path)
    await training_store.open()
    for record in records:
        training_store.add(Record.decode(record))

    await training_store.close()

    stored_records = [json.loads(line) for line in training_path.read_text().splitlines()]
    assert stored_records == records


async def test_add_appends_to_existing_records(training_path: Path) -> None:
    for _ in range(2):
        training_store = TrainingStore(training_path)
        await training_store.open()
        training_store.add(Record.decode(TRAINING_RECORD))
        await training_store.close()

    stored_records = [json.loads(line) for line in training_path.read_text().splitlines()]
    assert stored_records == [TRAINING_RECORD, TRAINING_RECORD]


async def test_add_after_close(training_path: Path) -> None:
    training_store = TrainingStore(training_path)
    await training_store.open()
    await training_store.close()

    with pytest.raises(asyncio.QueueShutDown):
        training_store.add(Record.decode(TRAINING_RECORD))


async def test_close_twice(training_path: Path) -> None:
    training_store = TrainingStore(training_path)
    await training_store.open()

    await training_store.close()
    await training_store.close()
