from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

import pytest
from quart import Quart

from tests.data import STATE
from walker.api.http.error import HTTPError


@pytest.mark.parametrize(
    ("state", "expected_response_status_code", "expected_response"),
    [
        pytest.param(
            STATE,
            HTTPStatus.OK,
            {"x": 0.0, "y": 0.0, "z": 0.0},
            id="200",
        ),
        pytest.param(
            {},
            HTTPError.INVALID_JSON.status,
            HTTPError.INVALID_JSON.as_dict(),
            id="400-empty",
        ),
        pytest.param(
            {"collisions": STATE["collisions"]},
            HTTPError.INVALID_JSON.status,
            HTTPError.INVALID_JSON.as_dict(),
            id="400-missing-fields",
        ),
        pytest.param(
            STATE | {"speed": {"x": "fast", "y": 0.0, "z": 0.0}},
            HTTPError.INVALID_JSON.status,
            HTTPError.INVALID_JSON.as_dict(),
            id="400-field-type",
        ),
    ],
)
async def test_generate_walk(
    walks_app: Quart,
    state: Mapping[str, Any],
    expected_response_status_code: int,
    expected_response: Mapping[str, Any],
) -> None:
    async with walks_app.test_client() as test_client:
        response = await test_client.post("/walks", json=state)

    assert response.status_code == expected_response_status_code
    assert await response.get_json() == expected_response


async def test_generate_walks(walks_app: Quart) -> None:
    test_client = walks_app.test_client()

    async with test_client.websocket("/walks") as test_websocket:
        for _ in range(2):
            await test_websocket.send_json(STATE)

            assert await test_websocket.receive_json() == {"x": 0.0, "y": 0.0, "z": 0.0}
