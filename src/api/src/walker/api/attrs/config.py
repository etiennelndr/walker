"""Configuration attribute constants module."""

from enum import auto

from ._base import Attrs


class App(Attrs):
    """Top-level application configuration keys."""

    ASGI = auto()
    """ASGI server configuration"""
    LOGGING = auto()
    """Logging configuration"""
    OPENAPI = auto()
    """OpenAPI specification configuration"""
    TRAINING = auto()
    """Training states configuration"""


class ASGI(Attrs):
    """ASGI server configuration keys."""

    HOST = auto()
    """The host address to bind the server to"""
    PORT = auto()
    """The port number to bind the server to"""
    LOOP = auto()
    """The event loop implementation to use"""
    HTTP = auto()
    """The HTTP protocol implementation to use"""
    WS = auto()
    """The WebSocket protocol implementation to use"""
    LIFESPAN = auto()
    """The Lifespan protocol implementation to use"""
    ACCESS_LOG = auto()
    """Whether to activate access logs or not"""
    INTERFACE = auto()
    """The ASGI interface to use"""
    WORKERS = auto()
    """The number of worker processes to spawn"""
    FORWARDED_ALLOW_IPS = auto()
    """List of IP Addresses, IP Networks, or literals (e.g. UNIX Socket path) to trust with proxy
    headers
    """


class Logging(Attrs):
    """Logging configuration keys."""

    DESTINATION = auto()
    """Where log messages should be written"""
    LEVEL = auto()
    """The minimum logging level for messages to be recorded"""
    STRUCTURED = auto()
    """Whether log messages are written as JSON objects or not"""


class OpenAPI(Attrs):
    """OpenAPI specification configuration keys."""

    ENDPOINT = auto()
    """The URL path where the OpenAPI specification is served"""


class Training(Attrs):
    """Training states configuration keys."""

    PATH = auto()
    """The file in which collected training states are stored"""


__all__ = [
    "App",
    "ASGI",
    "Logging",
    "OpenAPI",
    "Training",
]
