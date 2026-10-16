"""Application configuration."""

from collections.abc import Mapping
from logging import getLevelNamesMapping
from typing import Any, Final

from confuse import Choice, OneOf, Optional, Sequence

from walker.api.attrs.config import ASGI, App, Logging, OpenAPI, Training
from walker.config import templates

APP_CONFIG_TEMPLATE: Final[Mapping[str, Any]] = {
    App.ASGI: {
        ASGI.HOST: Optional(str, default="127.0.0.1"),
        ASGI.PORT: Optional(int, default=8000),
        ASGI.WORKERS: Optional(int, default=1),
        ASGI.ACCESS_LOG: Optional(bool, default=True),
        ASGI.LOOP: Choice(["none", "auto", "asyncio", "uvloop"], default="auto"),
        ASGI.HTTP: Choice(["auto", "h11", "httptools"], default="auto"),
        ASGI.WS: Choice(
            ["auto", "none", "websockets", "websockets-sansio", "wsproto"], default="auto"
        ),
        ASGI.LIFESPAN: Choice(["auto", "on", "off"], default="on"),
        ASGI.INTERFACE: Choice(["auto", "asgi3", "asgi2", "wsgi"], default="asgi3"),
        ASGI.FORWARDED_ALLOW_IPS: OneOf([str, Sequence(str)], default=None),
    },
    App.LOGGING: {
        Logging.DESTINATION: Optional(str, default="-"),
        Logging.LEVEL: Choice(list(getLevelNamesMapping())),
        Logging.STRUCTURED: Optional(bool, default=False),
    },
    App.OPENAPI: {
        OpenAPI.ENDPOINT: Optional(str),
    },
    App.TRAINING: {
        Training.PATH: templates.Path(default=None),
    },
}

__all__ = ["APP_CONFIG_TEMPLATE"]
