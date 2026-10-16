"""Helpers to access to file or class attributes."""

from enum import auto

from . import config
from ._base import Attrs


class Extensions(Attrs):
    """Keys of the application extensions."""

    TRAINING_STORE = auto()
    """Storage of the training states collected by the application"""


__all__ = ["Extensions", "config"]
