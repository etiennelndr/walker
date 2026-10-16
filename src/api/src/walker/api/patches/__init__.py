"""A collection of patches required by the application."""

from . import quart_schema


def patchify() -> None:
    """Applies all patches required by the main application."""
    quart_schema.patchify()


__all__ = ["patchify"]
