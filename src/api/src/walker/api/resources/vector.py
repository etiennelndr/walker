import cupy as cp

from ._array import Array, ArrayMixin
from ._base import APIResource


class Vector3(APIResource, ArrayMixin):
    """Representation of 3D vectors and points."""

    x: float
    """Coordinate along the x axis"""
    y: float
    """Coordinate along the y axis"""
    z: float
    """Coordinate along the z axis"""

    def as_array(self) -> Array:
        """Converts this vector to an array of shape ``(3,)``."""
        return cp.asarray([self.x, self.y, self.z], dtype=cp.float32)


__all__ = ["Vector3"]
