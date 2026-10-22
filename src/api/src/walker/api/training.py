"""Storage of the training states collected by the application."""

import asyncio
from pathlib import Path
from typing import BinaryIO, Self

from loguru import logger

from walker.core.resources.state import State


class TrainingStore:
    """Append-only storage of training states.

    States are stored in a JSON Lines file, one state per line.

    Adding a state only puts it in a queue: a background task takes the queued states and writes
    them to the file by batches, in a separate thread to not block the event loop. States still
    queued when the application stops unexpectedly are lost.
    """

    def __init__(self, path: Path) -> None:
        """Initializes the storage.

        :param path: JSON Lines file in which states are stored.
        """
        self._path = path
        self._queue: asyncio.Queue[State] = asyncio.Queue()
        self._writer: asyncio.Task[None] | None = None

    async def open(self) -> Self:
        """Opens the storage, creating its file if it does not exist."""
        logger.info(f"Storing training states in '{self._path}'")
        file = await asyncio.to_thread(self._path.open, "ab")
        self._writer = asyncio.create_task(self._write_states(file))
        return self

    async def close(self) -> None:
        """Closes the storage, once all the queued states are written.

        :raises OSError: if writing states to the file failed.
        """
        if self._writer is None:
            return

        # Let the writer end once the queue is empty
        self._queue.shutdown()
        try:
            await self._writer
        finally:
            self._writer = None

    def add(self, state: State) -> None:
        """Queues a state to be written to the storage.

        :param state: training state to store.
        :raises asyncio.QueueShutDown: if the storage is closed.
        """
        self._queue.put_nowait(state)

    async def _write_states(self, file: BinaryIO) -> None:
        """Writes the queued states to the file until the queue is shut down.

        :param file: file in which states are written. It is closed when this task ends.
        """
        with file:
            while True:
                try:
                    states = [await self._queue.get()]
                except asyncio.QueueShutDown:
                    break

                # Write all the states already queued in a single batch
                while not self._queue.empty():
                    states.append(self._queue.get_nowait())

                lines = b"".join(state.encode() + b"\n" for state in states)
                await asyncio.to_thread(self._write, file, lines)

    @staticmethod
    def _write(file: BinaryIO, data: bytes) -> None:
        """Writes data to a file and flushes it."""
        file.write(data)
        file.flush()


__all__ = ["TrainingStore"]
