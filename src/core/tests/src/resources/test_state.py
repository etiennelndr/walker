from tests.data import STATE
from walker.core.resources.ray import Ray, RayCollision
from walker.core.resources.state import State
from walker.core.resources.vector import Vector3


def test_decode() -> None:
    state = State.decode(STATE)

    assert state == State(
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
        speed=Vector3(x=1.5, y=0.0, z=-0.5),
    )


def test_encode() -> None:
    state = State.decode(STATE)

    assert State.decode(state.encode()) == state
