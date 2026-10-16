import cupy as cp
import pytest

from tests.data import STATE
from walker.api.resources import APIResource
from walker.api.resources._array import ArrayMixin
from walker.api.resources.ray import Ray, RayCollision
from walker.api.resources.state import State
from walker.api.resources.vector import Vector3


def assert_array(array: cp.ndarray, expected: list[float]) -> None:
    """Asserts an array is a flat array of 32-bit floats with the expected values."""
    assert isinstance(array, cp.ndarray)
    assert array.dtype == cp.float32
    assert array.tolist() == expected


def test_as_array_is_abstract() -> None:
    class Resource(APIResource, ArrayMixin):
        a: float

    with pytest.raises(TypeError, match="abstract method 'as_array'"):
        Resource(a=1.0)


def test_vector_as_array() -> None:
    vector = Vector3(x=1.5, y=0.0, z=-0.5)

    assert_array(vector.as_array(), [1.5, 0.0, -0.5])


def test_ray_as_array() -> None:
    ray = Ray.decode(STATE["collisions"][0]["ray"])

    assert_array(ray.as_array(), [0.0, 1.0, 0.0, 1.0, 0.0, 0.0])


def test_ray_collision_as_array() -> None:
    collision = RayCollision.decode(STATE["collisions"][0])

    assert_array(collision.as_array(), [0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 5.0, 1.0, 0.0])


def test_state_as_array() -> None:
    state = State.decode(STATE)

    assert_array(
        state.as_array(),
        [
            # First collision
            *[0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 5.0, 1.0, 0.0],
            # Second collision
            *[0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 2.5],
            # Speed
            *[1.5, 0.0, -0.5],
        ],
    )
