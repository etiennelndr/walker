from ._base import Resource


class Vector3(Resource):
    """Representation of 3-dimensional vectors."""

    x: float
    """Coordinate along the x axis"""
    y: float
    """Coordinate along the y axis"""
    z: float
    """Coordinate along the z axis"""


__all__ = ["Vector3"]
