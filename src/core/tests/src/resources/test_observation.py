from tests.data import OBSERVATION
from walker.core.resources.observation import Observation
from walker.core.resources.ray import Ray, RayCollision
from walker.core.resources.vector import Vector3


def test_decode() -> None:
    observation = Observation.decode(OBSERVATION)

    assert observation == Observation(
        collisions=[
            RayCollision(
                ray=Ray(
                    origin=Vector3(x=0.0, y=1.0, z=0.0),
                    direction=Vector3(x=1.0, y=0.0, z=0.0),
                ),
                point=Vector3(x=5.0, y=1.0, z=0.0),
            ),
            RayCollision(
                ray=Ray(
                    origin=Vector3(x=0.0, y=1.0, z=0.0),
                    direction=Vector3(x=0.0, y=0.0, z=1.0),
                ),
                point=Vector3(x=0.0, y=1.0, z=2.5),
            ),
        ],
        velocity=Vector3(x=1.5, y=0.0, z=-0.5),
    )


def test_encode() -> None:
    observation = Observation.decode(OBSERVATION)

    assert Observation.decode(observation.encode()) == observation
