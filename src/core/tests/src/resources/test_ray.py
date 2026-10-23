import json
from typing import Any

import pytest

from walker.core.resources import ResourceDecodingError
from walker.core.resources.ray import Ray, RayCollision
from walker.core.resources.vector import Vector3

RAY: dict[str, Any] = {
    "origin": {"x": 0.0, "y": 1.0, "z": 0.0},
    "direction": {"x": 1.0, "y": 0.0, "z": 0.0},
}
RAY_COLLISION: dict[str, Any] = {
    "ray": RAY,
    "point": {"x": 5.0, "y": 1.0, "z": 0.0},
}


def test_decode_ray() -> None:
    assert Ray.decode(json.dumps(RAY)) == Ray(
        origin=Vector3(x=0.0, y=1.0, z=0.0),
        direction=Vector3(x=1.0, y=0.0, z=0.0),
    )


def test_decode_ray_collision() -> None:
    assert RayCollision.decode(json.dumps(RAY_COLLISION)) == RayCollision(
        ray=Ray(
            origin=Vector3(x=0.0, y=1.0, z=0.0),
            direction=Vector3(x=1.0, y=0.0, z=0.0),
        ),
        point=Vector3(x=5.0, y=1.0, z=0.0),
    )


@pytest.mark.parametrize(
    ("resource_class", "data"),
    [
        pytest.param(Ray, RAY, id="ray"),
        pytest.param(RayCollision, RAY_COLLISION, id="ray-collision"),
    ],
)
def test_encode(resource_class: type[Ray | RayCollision], data: dict[str, Any]) -> None:
    resource = resource_class.decode(data)

    assert json.loads(resource.encode()) == data


@pytest.mark.parametrize(
    ("resource_class", "data"),
    [
        pytest.param(Ray, {"origin": RAY["origin"]}, id="ray-missing-field"),
        pytest.param(
            Ray,
            RAY | {"direction": {"x": 1.0, "y": 0.0}},
            id="ray-invalid-vector",
        ),
        pytest.param(RayCollision, {"ray": RAY}, id="ray-collision-missing-field"),
        pytest.param(
            RayCollision,
            RAY_COLLISION | {"ray": {"origin": RAY["origin"]}},
            id="ray-collision-invalid-ray",
        ),
    ],
)
def test_decode_invalid(resource_class: type[Ray | RayCollision], data: dict[str, Any]) -> None:
    with pytest.raises(ResourceDecodingError):
        resource_class.decode(json.dumps(data))
