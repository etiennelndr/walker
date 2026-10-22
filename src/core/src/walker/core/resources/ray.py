from ._base import Resource
from .vector import Vector3


class Ray(Resource):
    """An infinite line going in some direction."""

    origin: Vector3
    """Origin of the ray"""
    direction: Vector3
    """Direction of the ray"""


class RayCollision(Resource):
    """Representation of the collision between a ray and a collider."""

    ray: Ray
    """Ray that hit the collider"""
    point: Vector3
    """Point where the ray hit the collider"""


__all__ = ["Ray", "RayCollision"]
