"""Internal utilities for the patches."""

from collections.abc import Callable
from types import FunctionType


def copy_function[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Creates a shallow copy of a function.

    :param func: the function to copy.
    :returns: a shallow copy of the function.
    :raises TypeError: if ``func`` is not a function.
    """
    if not isinstance(func, FunctionType):
        raise TypeError(f"Expected a function, got {type(func).__name__!r}")

    return type(func)(
        func.__code__,
        func.__globals__.copy(),
        func.__name__,
        func.__defaults__,
        func.__closure__,
        func.__kwdefaults__,
    )


__all__ = ["copy_function"]
