import cupy as cp

from ._array import Array, ArrayMixin
from ._base import APIResource
from .vector import Vector3


class Ray(APIResource, ArrayMixin):
    """An infinite line going in some direction."""

    origin: Vector3
    """Origin of the ray"""
    direction: Vector3
    """Direction of the ray"""

    def as_array(self) -> Array:
        """Converts this ray to an array of shape ``(6,)``: its origin, then its direction."""
        return cp.concatenate(
            [self.origin.as_array(), self.direction.as_array()],
            dtype=cp.float32,
        )


class RayCollision(APIResource, ArrayMixin):
    """Representation of the collision between a ray and a collider."""

    ray: Ray
    """Ray that hit the collider"""
    point: Vector3
    """Point where the ray hit the collider"""

    def as_array(self) -> Array:
        """Converts this collision to an array of shape ``(9,)``: its ray, then its point."""
        return cp.concatenate(
            [self.ray.as_array(), self.point.as_array()],
            dtype=cp.float32,
        )


__all__ = ["Ray", "RayCollision"]
