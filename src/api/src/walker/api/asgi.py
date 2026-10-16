"""ASGI server lifecycle module.

This module provides functionalities to create and configure an ASGI server using Uvicorn to run the
application in an asynchronous event loop.
"""

import asyncio
import logging
from collections.abc import Iterable
from signal import SIGINT, SIGTERM, Signals
from types import FrameType

import uvicorn
from loguru import logger
from quart import Quart

import walker.config as wc

from . import attrs
from .asyncio.loop import register_signal_handler
from .logging import deactivate_logger

# Disable default behaviour where Uvicorn registers its handlers and prevents stopping the main
# event loop. Because of this, Uvicorn shutdown shall be handled by the user.
uvicorn.server.HANDLED_SIGNALS = tuple()  # type: ignore


class ASGIServer(uvicorn.Server):
    """Prevents automatic signal re-propagation during the server shutdown sequence.

    External orchestration handles signal management, making Uvicorn's default signal buffering
    redundant and potentially harmful in this context.
    """

    def handle_exit(self, sig: int, frame: FrameType | None) -> None:
        """Sets the internal exit flags upon signal reception without buffering for re-raising.

        Storage in the internal buffer is omitted to avoid duplicate signal delivery after the
        server process terminates.

        :param sig: signal that initiated the exit.
        :param frame: current stack frame at the time the signal was received.
        """
        if self.should_exit and sig == SIGINT:
            self.force_exit = True
        else:
            self.should_exit = True


def create_asgi_server(app: Quart) -> ASGIServer:
    """Creates a Uvicorn ASGI server configured from the application settings.

    Uvicorn's default loggers are replaced by the application's logger handlers.

    Multi-worker mode is not supported.

    :param app: application instance to be served.
    :returns: configured Uvicorn server ready to serve the application.
    :raises KeyError: if the ASGI configuration is missing from the application config.
    :raises ValueError: if the number of configured workers is greater than one.
    """
    server_config = uvicorn.Config(app, **wc.get(app.config, attrs.config.App.ASGI))
    if server_config.workers > 1:
        raise ValueError(
            f"Multi-worker mode is not supported (got {server_config.workers} workers). Set the"
            f" number of workers to 1 in the ASGI configuration."
        )

    deactivate_logger(logging.getLogger("uvicorn"))
    # Overwrites Uvicorn loggers with the application's one
    for uvicorn_logger_name in (
        "uvicorn.access",
        "uvicorn.asgi",
        "uvicorn.error",
    ):
        logging.getLogger(uvicorn_logger_name).handlers = list(app.logger.handlers)

    return ASGIServer(server_config)


class ASGIServerHandler:
    """Wraps an ASGI server to manage its serve and shutdown lifecycle."""

    def __init__(self, server: ASGIServer) -> None:
        """Initializes the handler with the given ASGI server.

        :param server: ASGI server instance to manage.
        """
        self._server = server
        self._server_event: asyncio.Event = asyncio.Event()

    @property
    def is_exiting(self) -> bool:
        """Indicates whether the ASGI server has already been asked to exit."""
        return self._server.should_exit or self._server.force_exit

    async def serve(self) -> None:
        """Starts the ASGI server and waits for its completion."""
        self._server_event.clear()
        try:
            await self._server.serve()
        finally:
            self._server_event.set()

    async def shutdown(self, signal: Signals, frame: FrameType | None = None) -> None:
        """Triggers a graceful shutdown of the ASGI server and waits for it to complete.

        :param signal: signal that initiated the shutdown.
        :param frame: current stack frame at the time the signal was received.
        """
        if self.is_exiting:
            logger.warning(
                f"ASGI server shutdown already initiated or completed, ignoring '{signal.name}'"
            )
            return

        logger.info(f"Shutting down ASGI server on signal '{signal.name}'")

        self._server.handle_exit(signal, frame)
        # Wait until ASGI server has finished its shutdown
        await self._server_event.wait()


async def serve_asgi_server_handlers(*server_handlers: ASGIServerHandler) -> None:
    """Serves multiple ASGI server handlers concurrently and registers shutdown signal handlers.

    Registers ``SIGINT`` and ``SIGTERM`` handlers to gracefully stop all servers on signal
    reception. As soon as one server stops, whether normally or on error, the remaining ones are
    shut down.

    :param server_handlers: server handlers to serve concurrently.
    :raises BaseException: any error raised by a server while serving.
    """
    register_signal_handler(
        SIGINT,
        shutdown_asgi_server_handlers,
        SIGINT,
        server_handlers,
    )
    register_signal_handler(
        SIGTERM,
        shutdown_asgi_server_handlers,
        SIGTERM,
        server_handlers,
    )

    server_tasks = [asyncio.create_task(sh.serve()) for sh in server_handlers]
    # Returns as soon as one server has stopped, whatever the reason
    await asyncio.wait(server_tasks, return_when=asyncio.FIRST_COMPLETED)
    # Stops the servers that are still running and not already shutting down
    await shutdown_asgi_server_handlers(
        SIGTERM,
        [
            sh
            for sh, task in zip(server_handlers, server_tasks)
            if not task.done() and not sh.is_exiting
        ],
    )
    # Propagates the error that stopped the server, if any
    await asyncio.gather(*server_tasks)


async def shutdown_asgi_server_handlers(
    signal: Signals,
    server_handlers: Iterable[ASGIServerHandler],
) -> None:
    """Shuts down all ASGI server handlers sequentially on signal reception.

    :param signal: emitted signal.
    :param server_handlers: server handlers to shut down.
    """
    await asyncio.gather(*[sh.shutdown(signal) for sh in server_handlers if not sh.is_exiting])


__all__ = [
    "ASGIServerHandler",
    "ASGIServer",
    "create_asgi_server",
    "serve_asgi_server_handlers",
    "shutdown_asgi_server_handlers",
]
