"""Asyncio event loop utilities."""

import signal as signals
from asyncio import AbstractEventLoop, get_running_loop
from collections.abc import Awaitable, Callable
from inspect import iscoroutinefunction
from signal import Signals


def register_signal_handler[*Ha](
    signal: Signals,
    handler: Callable[[*Ha], None] | Callable[[*Ha], Awaitable[None]],
    *handler_args: *Ha,
    loop: AbstractEventLoop | None = None,
) -> None:
    """Registers a signal handler on the event loop, supporting both sync and async callables.

    If ``handler`` is a coroutine function, it is scheduled as a task in the running event loop
    when the signal is received.

    Event loops that cannot handle signals (e.g. the ones available on Windows) fall back to
    :py:func:`signal.signal`, the handler being then scheduled on the event loop from the main
    thread.

    :param signal: signal to handle.
    :param handler: callable invoked when ``signal`` is received.
    :param handler_args: positional arguments forwarded to ``handler``.
    :param loop: event loop on which the handler is registered. Defaults to the running loop if
        ``None``.
    :raises RuntimeError: if ``loop`` is ``None`` and no running event loop exists.
    """
    if loop is None:
        loop = get_running_loop()

    def _handle_signal() -> None:
        if iscoroutinefunction(handler):
            loop.create_task(handler(*handler_args))
        else:
            handler(*handler_args)

    try:
        loop.add_signal_handler(signal, _handle_signal)
    except NotImplementedError:
        signals.signal(signal, lambda *_: loop.call_soon_threadsafe(_handle_signal))


__all__ = ["register_signal_handler"]
