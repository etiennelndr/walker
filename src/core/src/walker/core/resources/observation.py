from ._base import Resource
from .ray import RayCollision
from .vector import Vector3


class Observation(Resource):
    """Representation of what a walker observes at a given time."""

    collisions: list[RayCollision]
    """Collisions between the rays cast by the walker and its surroundings"""
    velocity: Vector3
    """Current velocity of the walker"""


__all__ = ["Observation"]
