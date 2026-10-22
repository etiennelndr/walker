from ._base import Resource
from .ray import RayCollision
from .vector import Vector3


class State(Resource):
    """Representation of a walker state."""

    collisions: list[RayCollision]
    """Collisions between the rays cast by the walker and its surroundings"""
    speed: Vector3
    """Current speed of the walker"""


__all__ = ["State"]
