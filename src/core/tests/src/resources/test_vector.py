import json
from typing import Any

import pytest

from walker.core.resources import ResourceDecodingError
from walker.core.resources.vector import Vector3


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({"x": 1.5, "y": 0.0, "z": -2.0}, id="floats"),
        pytest.param({"x": 1.5, "y": 0, "z": -2}, id="integers"),
    ],
)
def test_decode(data: dict[str, Any]) -> None:
    assert Vector3.decode(json.dumps(data)) == Vector3(x=1.5, y=0.0, z=-2.0)


def test_encode() -> None:
    vector = Vector3(x=1.5, y=0.0, z=-2.0)

    assert vector.encode() == b'{"x":1.5,"y":0.0,"z":-2.0}'


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({}, id="empty"),
        pytest.param({"x": 1.5, "y": 0.0}, id="missing-field"),
        pytest.param({"x": "fast", "y": 0.0, "z": -2.0}, id="field-type"),
    ],
)
def test_decode_invalid(data: dict[str, Any]) -> None:
    with pytest.raises(ResourceDecodingError):
        Vector3.decode(json.dumps(data))
