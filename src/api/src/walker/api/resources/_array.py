"""Module for converting API resources to arrays."""

from abc import ABC, abstractmethod

import cupy as cp
import cupy.typing as cpt

type Array = cpt.NDArray[cp.float32]
"""An array of 32-bit floats, stored on the GPU"""


class ArrayMixin(ABC):
    """Mixin for the API resources that can be converted to arrays."""

    # Without empty slots, the resources using this mixin would get a `__dict__`, which API
    # resources avoid to stay compact
    __slots__ = ()

    @abstractmethod
    def as_array(self) -> Array:
        """Converts this resource to a flat array of 32-bit floats, stored on the GPU."""


__all__ = ["Array", "ArrayMixin"]
