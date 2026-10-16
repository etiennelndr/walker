import cupy as cp

from ._array import Array, ArrayMixin
from ._base import APIResource
from .ray import RayCollision
from .vector import Vector3


class State(APIResource, ArrayMixin):
    """Representation of a walker state."""

    collisions: list[RayCollision]
    """Collisions between the rays cast by the walker and its surroundings"""
    speed: Vector3
    """Current speed of the walker"""

    def as_array(self) -> Array:
        """Converts this state to a flat array of features.

        The array holds the 9 values of each collision, followed by the 3 values of the speed. Its
        shape is ``(9 * len(collisions) + 3,)``.
        """
        return cp.concatenate(
            [
                *(collision.as_array() for collision in self.collisions),
                self.speed.as_array(),
            ],
            dtype=cp.float32,
        )


__all__ = ["State"]
