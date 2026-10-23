from uuid import UUID

from ._base import Resource
from .observation import Observation
from .vector import Vector3


class Record(Resource, omit_defaults=True):
    """Representation of a walker record.

    A record holds an observation of a walker along with what is needed to train or evaluate the
    models with it. Fields that do not apply to the behaviour of the walker are left empty and are
    not encoded.
    """

    session: UUID
    """Identifier generated when the simulation starts, shared by all its walkers"""
    walker: str
    """Identifier of the walker, unique within a session"""
    scene: str
    """Name of the scene in which the walker moves"""
    frame: int
    """Number of the frame at which the observation was collected"""
    time: float
    """Time at which the observation was collected, in seconds since the simulation started"""
    observation: Observation
    """Observation of the walker, i.e. the input of the models"""
    # Training fields
    desired_velocity: Vector3 | None = None
    """Velocity the walker intends to reach, i.e. the answer expected from the models"""
    target: Vector3 | None = None
    """Position of the point the walker heads to"""
    # Patrolling fields
    contacts: int | None = None
    """Number of contacts between the walker and an obstacle since the previous record"""
    walk: Vector3 | None = None
    """Last velocity returned by the API, i.e. the one applied to the walker"""


__all__ = ["Record"]
