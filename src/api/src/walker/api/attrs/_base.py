"""Attribute constants base module.

This module provides a helper for accessing elements from files, classes, dictionaries, etc.
Elements are organized into logical groups representing different aspects of the application.
"""

from enum import StrEnum


class Attrs(StrEnum):
    """Base class for attribute enumerations."""


__all__ = ["Attrs"]
