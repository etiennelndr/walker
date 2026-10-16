"""Internal utility functions."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Final, cast

if TYPE_CHECKING:
    from .core import ConfigKey


_SNAKE_TO_FLAT_CASE_PATTERN: Final = re.compile(r"_([a-z]+)")


def snake_to_flat_case(text: str) -> str:
    """Converts snake case to flat case.

    Result is only guaranteed if input string is valid snake_case.

    :Example:

    >>> snake_to_flat_case("input_text")
    'inputtext'

    :param text: input text to transform.
    :returns: flat case text.
    """
    return _SNAKE_TO_FLAT_CASE_PATTERN.sub(lambda m: m.group(1), text)


type NestedIterable[T] = Iterable[T] | Iterable[NestedIterable[T]]


def flatten[T](elements: NestedIterable[T]) -> Iterable[T]:
    """Recursively flattens a nested iterable into a single-level iterable.

    This function takes an iterable that may contain nested iterables (such as lists or tuples) and
    yields each element in a flat, one-dimensional sequence. :py:class:`str` are treated as atomic
    elements and are not expanded into individual characters.

    :param elements: an iterable that may contain elements or nested iterables of arbitrary depth.
    :returns: a flattened iterable that yields all non-iterable elements in depth-first order.

    :Example:

    >>> list(flatten([1, [2, 3], [[4], 5], "abc"]))
    [1, 2, 3, 4, 5, 'abc']
    >>> list(flatten(((1, 2), (3, (4, 5)))))
    [1, 2, 3, 4, 5]
    """
    for element in elements:
        if isinstance(element, Iterable) and not isinstance(element, Mapping | str):
            yield from flatten(element)
        else:
            yield cast(T, element)


def concatenate_keys(*keys: ConfigKey | Sequence[ConfigKey]) -> str:
    """Concatenates the given `keys` using `.`.

    :Example:

    >>> concatenate_keys(["logging"])
    'logging'
    >>> concatenate_keys(["logging", "debug"])
    'logging.debug'
    """
    return ".".join(
        # Flatten keys before joining them
        flatten(keys)
    )


__all__ = ["NestedIterable", "concatenate_keys", "flatten", "snake_to_flat_case"]
