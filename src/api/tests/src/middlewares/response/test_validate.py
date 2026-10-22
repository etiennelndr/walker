from collections.abc import Mapping
from http import HTTPStatus

import pytest
from quart import Blueprint, Quart

from walker.api import middlewares
from walker.api.http.error import HTTPError
from walker.api.resources.error import Error
from walker.api.typing import RouteResponseValue
from walker.core.resources import Resource


class Payload(Resource):
    id: int
    name: str
    elapsed_time: int


def register_endpoint[T: RouteResponseValue](app: Quart, response: T) -> None:
    tests_bp = Blueprint("tests", __name__, url_prefix="/tests")

    @tests_bp.get("/<int:test_id>")
    @middlewares.response(
        middlewares.res.validate(
            {
                HTTPStatus.OK: Payload,
                HTTPStatus.BAD_REQUEST: Error,
            }
        ),
    )
    async def get_test(test_id: int) -> T:
        if test_id == 0:
            HTTPError.INVALID_REQUEST.abort()
        return response

    app.register_blueprint(tests_bp)


@pytest.mark.parametrize(
    (
        "endpoint_response",
        "test_id",
        "expected_response_status_code",
        "expected_response",
    ),
    [
        pytest.param(
            {
                "id": 1,
                "name": "Hector",
                "elapsed_time": 60,
            },
            1,
            HTTPStatus.OK,
            {
                "id": 1,
                "name": "Hector",
                "elapsed_time": 60,
            },
            id="200-mapping",
        ),
        pytest.param(
            Payload(
                id=1,
                name="Hector",
                elapsed_time=60,
            ),
            1,
            HTTPStatus.OK,
            {
                "id": 1,
                "name": "Hector",
                "elapsed_time": 60,
            },
            id="200-resource",
        ),
        pytest.param(
            {},
            0,
            HTTPError.INVALID_REQUEST.status,
            HTTPError.INVALID_REQUEST.as_dict(),
            id="400-id",
        ),
        pytest.param(
            {},
            1,
            HTTPError.INTERNAL_ERROR.status,
            HTTPError.INTERNAL_ERROR.as_dict(),
            id="500-empty",
        ),
        pytest.param(
            {
                "id": 1,
                "name": 1234,
                "elapsed_time": 60,
            },
            1,
            HTTPError.INTERNAL_ERROR.status,
            HTTPError.INTERNAL_ERROR.as_dict(),
            id="500-field-type",
        ),
        pytest.param(
            "CPT",
            1,
            HTTPError.INTERNAL_ERROR.status,
            HTTPError.INTERNAL_ERROR.as_dict(),
            id="500-type",
        ),
        pytest.param(
            Error(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="CPT",
                code="TREVELL-API-0123",
            ),
            1,
            HTTPError.INTERNAL_ERROR.status,
            HTTPError.INTERNAL_ERROR.as_dict(),
            id="500-resource-type",
        ),
    ],
)
async def test_validate(
    app: Quart,
    endpoint_response: Mapping,
    test_id: int,
    expected_response_status_code: int,
    expected_response: Mapping,
) -> None:
    register_endpoint(app, endpoint_response)

    async with app.test_client() as test_client:
        response = await test_client.get(f"/tests/{test_id}")

    assert response.status_code == expected_response_status_code
    assert await response.get_json() == expected_response
