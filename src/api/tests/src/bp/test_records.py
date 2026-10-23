import json
from collections.abc import Mapping
from http import HTTPStatus
from pathlib import Path
from typing import Any

import pytest
from quart import Quart

from tests.data import TRAINING_RECORD
from tests.fixtures import serve_app
from walker.api.bp.records import records_bp
from walker.api.http.error import HTTPError


@pytest.mark.usefixtures("environment_variables")
async def test_create_record(training_path: Path) -> None:
    records = [TRAINING_RECORD, TRAINING_RECORD | {"frame": 43, "time": 4.3}]

    async with serve_app(records_bp) as records_app:
        async with records_app.test_client() as test_client:
            for record in records:
                response = await test_client.post("/records", json=record)

                assert response.status_code == HTTPStatus.CREATED
                assert await response.get_json() == record

    # Records are stored once the application is shut down, one per line
    stored_records = [json.loads(line) for line in training_path.read_text().splitlines()]
    assert stored_records == records


@pytest.mark.parametrize(
    "record",
    [
        pytest.param({}, id="empty"),
        pytest.param({"observation": TRAINING_RECORD["observation"]}, id="missing-fields"),
        pytest.param(TRAINING_RECORD | {"frame": "first"}, id="field-type"),
        pytest.param(TRAINING_RECORD | {"session": "session"}, id="session-format"),
    ],
)
async def test_create_record_invalid(
    records_app: Quart,
    training_path: Path,
    record: Mapping[str, Any],
) -> None:
    async with records_app.test_client() as test_client:
        response = await test_client.post("/records", json=record)

    assert response.status_code == HTTPError.INVALID_JSON.status
    assert await response.get_json() == HTTPError.INVALID_JSON.as_dict()
    assert training_path.read_text() == ""
