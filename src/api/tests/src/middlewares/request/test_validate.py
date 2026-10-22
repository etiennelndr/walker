from collections.abc import Mapping
from http import HTTPStatus

import pytest
from quart import Blueprint, Quart

from walker.api import middlewares
from walker.api.http.error import HTTPError
from walker.core.resources import Resource


class Payload(Resource):
    id: int
    name: str
    elapsed_time: int


def register_endpoint(app: Quart) -> None:
    tests_bp = Blueprint("tests", __name__, url_prefix="/tests")

    @tests_bp.post("")
    @middlewares.request(
        middlewares.req.validate(data=Payload),
    )
    async def create_test(data: Payload) -> Mapping:
        return {"id": data.id}

    app.register_blueprint(tests_bp)


@pytest.mark.parametrize(
    (
        "endpoint_request",
        "expected_response_status_code",
        "expected_response",
    ),
    [
        pytest.param(
            {
                "id": 2,
                "name": "Hector",
                "elapsed_time": 60,
            },
            HTTPStatus.OK,
            {"id": 2},
            id="200",
        ),
        pytest.param(
            {"id": 1, "name": "Hector", "elapsed_time": 60, "extra": "wechwech"},
            HTTPStatus.OK,
            {"id": 1},
            id="200-extra",
        ),
        pytest.param(
            {},
            HTTPError.INVALID_JSON.status,
            HTTPError.INVALID_JSON.as_dict(),
            id="400-empty",
        ),
        pytest.param(
            {
                "id": 2,
            },
            HTTPError.INVALID_JSON.status,
            HTTPError.INVALID_JSON.as_dict(),
            id="400-missing-fields",
        ),
        pytest.param(
            {
                "id": 2,
                "extra": "holahola",
            },
            HTTPError.INVALID_JSON.status,
            HTTPError.INVALID_JSON.as_dict(),
            id="400-missing-fields-with-extra",
        ),
        pytest.param(
            {
                "id": 1,
                "name": "Hector",
                "elapsedTime": 60,
            },
            HTTPError.INVALID_JSON.status,
            HTTPError.INVALID_JSON.as_dict(),
            id="400-no-snakecase",
        ),
        pytest.param(
            {
                "id": 1,
                "name": 1234,
                "elapsed_time": 60,
            },
            HTTPError.INVALID_JSON.status,
            HTTPError.INVALID_JSON.as_dict(),
            id="400-field-type",
        ),
        pytest.param(
            '"CPT"',
            HTTPError.INVALID_JSON.status,
            HTTPError.INVALID_JSON.as_dict(),
            id="400-type",
        ),
    ],
)
async def test_validate(
    app: Quart,
    endpoint_request: Mapping,
    expected_response_status_code: int,
    expected_response: Mapping,
) -> None:
    register_endpoint(app)

    async with app.test_client() as test_client:
        response = await test_client.post("/tests", json=endpoint_request)

    assert response.status_code == expected_response_status_code
    assert await response.get_json() == expected_response
