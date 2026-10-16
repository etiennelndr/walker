import json
from collections.abc import Mapping
from http import HTTPStatus
from pathlib import Path
from typing import Any

import pytest
from quart import Quart

from tests.data import STATE
from tests.fixtures import serve_app
from walker.api.bp.states import states_bp
from walker.api.http.error import HTTPError


@pytest.mark.usefixtures("environment_variables")
async def test_create_state(training_path: Path) -> None:
    states = [STATE, STATE | {"speed": {"x": 0.0, "y": 0.0, "z": 0.0}}]

    async with serve_app(states_bp) as states_app:
        async with states_app.test_client() as test_client:
            for state in states:
                response = await test_client.post("/states", json=state)

                assert response.status_code == HTTPStatus.CREATED
                assert await response.get_json() == state

    # States are stored once the application is shut down, one per line
    stored_states = [json.loads(line) for line in training_path.read_text().splitlines()]
    assert stored_states == states


@pytest.mark.parametrize(
    "state",
    [
        pytest.param({}, id="empty"),
        pytest.param({"collisions": STATE["collisions"]}, id="missing-fields"),
        pytest.param(
            STATE | {"speed": {"x": "fast", "y": 0.0, "z": 0.0}},
            id="field-type",
        ),
    ],
)
async def test_create_state_invalid(
    states_app: Quart,
    training_path: Path,
    state: Mapping[str, Any],
) -> None:
    async with states_app.test_client() as test_client:
        response = await test_client.post("/states", json=state)

    assert response.status_code == HTTPError.INVALID_JSON.status
    assert await response.get_json() == HTTPError.INVALID_JSON.as_dict()
    assert training_path.read_text() == ""
