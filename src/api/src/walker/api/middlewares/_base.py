"""Base module for application middlewares."""

from collections.abc import Callable

from walker.api.typing import Route

type Middleware = Callable[[Route], Route]


__all__ = ["Middleware"]
