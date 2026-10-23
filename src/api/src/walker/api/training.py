"""Storage of the training records collected by the application."""

import asyncio
from pathlib import Path
from typing import BinaryIO, Self

from loguru import logger

from walker.core.resources.record import Record


class TrainingStore:
    """Append-only storage of training records.

    Records are stored in a JSON Lines file, one record per line.

    Adding a record only puts it in a queue: a background task takes the queued records and writes
    them to the file by batches, in a separate thread to not block the event loop. Records still
    queued when the application stops unexpectedly are lost.
    """

    def __init__(self, path: Path) -> None:
        """Initializes the storage.

        :param path: JSON Lines file in which records are stored.
        """
        self._path = path
        self._queue: asyncio.Queue[Record] = asyncio.Queue()
        self._writer: asyncio.Task[None] | None = None

    async def open(self) -> Self:
        """Opens the storage, creating its file if it does not exist."""
        logger.info(f"Storing training records in '{self._path}'")
        file = await asyncio.to_thread(self._path.open, "ab")
        self._writer = asyncio.create_task(self._write_records(file))
        return self

    async def close(self) -> None:
        """Closes the storage, once all the queued records are written.

        :raises OSError: if writing records to the file failed.
        """
        if self._writer is None:
            return

        # Let the writer end once the queue is empty
        self._queue.shutdown()
        try:
            await self._writer
        finally:
            self._writer = None

    def add(self, record: Record) -> None:
        """Queues a record to be written to the storage.

        :param record: training record to store.
        :raises asyncio.QueueShutDown: if the storage is closed.
        """
        self._queue.put_nowait(record)

    async def _write_records(self, file: BinaryIO) -> None:
        """Writes the queued records to the file until the queue is shut down.

        :param file: file in which records are written. It is closed when this task ends.
        """
        with file:
            while True:
                try:
                    records = [await self._queue.get()]
                except asyncio.QueueShutDown:
                    break

                # Write all the records already queued in a single batch
                while not self._queue.empty():
                    records.append(self._queue.get_nowait())

                lines = b"".join(record.encode() + b"\n" for record in records)
                await asyncio.to_thread(self._write, file, lines)

    @staticmethod
    def _write(file: BinaryIO, data: bytes) -> None:
        """Writes data to a file and flushes it."""
        file.write(data)
        file.flush()


__all__ = ["TrainingStore"]
