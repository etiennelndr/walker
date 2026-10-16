from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from quart import Quart
from quart import Response as QuartResponse
from werkzeug import Response as WerkzeugResponse
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException

from walker.api.route import pack_route_response, unpack_route_response

shared_headers = Headers([("X-Custom", "value")])
quart_response = MagicMock(spec=QuartResponse, status_code=HTTPStatus.OK, headers=shared_headers)
werkzeug_response = MagicMock(
    spec=WerkzeugResponse, status_code=HTTPStatus.OK, headers=shared_headers
)


@pytest.mark.parametrize(
    "response, expected",
    [
        # Single value — no status, no headers
        pytest.param(
            {"walker": "Jean-Michel Trottinette"},
            ({"walker": "Jean-Michel Trottinette"}, None, None),
            id="dict-alone",
        ),
        pytest.param("hello", ("hello", None, None), id="str-alone"),
        pytest.param(b"bytes", (b"bytes", None, None), id="bytes-alone"),
        pytest.param([1, 2, 3], ([1, 2, 3], None, None), id="list-alone"),
        # 2-tuple — value + status
        pytest.param(
            ({"walker": "Jean-Michel Trottinette"}, HTTPStatus.CREATED),
            ({"walker": "Jean-Michel Trottinette"}, HTTPStatus.CREATED, None),
            id="2-tuple-value-status",
        ),
        # 2-tuple — value + headers
        pytest.param(
            ({"walker": "Jean-Michel Trottinette"}, Headers([("X-Foo", "bar")])),
            ({"walker": "Jean-Michel Trottinette"}, None, Headers([("X-Foo", "bar")])),
            id="2-tuple-value-headers",
        ),
        # 3-tuple — value + status + headers
        pytest.param(
            (
                {"walker": "Jean-Michel Trottinette"},
                HTTPStatus.CREATED,
                Headers([("X-Foo", "bar")]),
            ),
            (
                {"walker": "Jean-Michel Trottinette"},
                HTTPStatus.CREATED,
                Headers([("X-Foo", "bar")]),
            ),
            id="3-tuple-value-status-headers",
        ),
    ],
)
def test_unpack_route_response(response, expected):
    result = unpack_route_response(response)
    assert result == expected


@pytest.mark.parametrize(
    "response",
    [
        pytest.param((), id="empty-tuple"),
        pytest.param(("value",), id="1-tuple"),
        pytest.param(("value", HTTPStatus.OK, Headers(), "extra"), id="4-tuple"),
    ],
)
async def test_unpack_route_response_invalid_tuple(app: Quart, response):
    async with app.app_context():
        with pytest.raises(HTTPException):
            unpack_route_response(response)


@pytest.mark.parametrize(
    (
        "response_value",
        "response_status",
        "response_headers",
        "expected",
    ),
    [
        # Plain values — no status, no headers
        pytest.param(
            {"walker": "Jean-Michel Trottinette"},
            None,
            None,
            {"walker": "Jean-Michel Trottinette"},
            id="dict-no-status-no-headers",
        ),
        pytest.param("hello", None, None, "hello", id="str-no-status-no-headers"),
        pytest.param(b"bytes", None, None, b"bytes", id="bytes-no-status-no-headers"),
        pytest.param([1, 2, 3], None, None, [1, 2, 3], id="list-no-status-no-headers"),
        # Plain values — with headers only
        pytest.param(
            {"walker": "Jean-Michel Trottinette"},
            None,
            Headers([("X-Foo", "bar")]),
            ({"walker": "Jean-Michel Trottinette"}, Headers([("X-Foo", "bar")])),
            id="dict-no-status-with-headers",
        ),
        # Plain values — with status only
        pytest.param(
            {"walker": "Jean-Michel Trottinette"},
            HTTPStatus.CREATED,
            None,
            ({"walker": "Jean-Michel Trottinette"}, HTTPStatus.CREATED),
            id="dict-with-status-no-headers",
        ),
        # Plain values — with both status and headers
        pytest.param(
            {"walker": "Jean-Michel Trottinette"},
            HTTPStatus.CREATED,
            Headers([("X-Foo", "bar")]),
            (
                {"walker": "Jean-Michel Trottinette"},
                HTTPStatus.CREATED,
                Headers([("X-Foo", "bar")]),
            ),
            id="dict-with-status-and-headers",
        ),
        # QuartResponse — status matches, headers are the same object → both dropped
        pytest.param(
            quart_response,
            HTTPStatus.OK,
            shared_headers,
            quart_response,
            id="quart-response-status-matches-headers-same-object",
        ),
        # QuartResponse — status matches → status dropped, headers kept
        pytest.param(
            quart_response,
            HTTPStatus.OK,
            Headers([("X-Other", "val")]),
            (quart_response, Headers([("X-Other", "val")])),
            id="quart-response-status-matches-headers-different",
        ),
        # QuartResponse — status differs, headers are the same object → headers dropped
        pytest.param(
            quart_response,
            HTTPStatus.CREATED,
            shared_headers,
            (quart_response, HTTPStatus.CREATED),
            id="quart-response-status-differs-headers-same-object",
        ),
        # QuartResponse — status differs, headers differ → both kept
        pytest.param(
            quart_response,
            HTTPStatus.CREATED,
            Headers([("X-Other", "val")]),
            (quart_response, HTTPStatus.CREATED, Headers([("X-Other", "val")])),
            id="quart-response-status-differs-headers-different",
        ),
        # WerkzeugResponse — status matches, headers are the same object → both dropped
        pytest.param(
            werkzeug_response,
            HTTPStatus.OK,
            shared_headers,
            werkzeug_response,
            id="werkzeug-response-status-matches-headers-same-object",
        ),
        # WerkzeugResponse — status matches → status dropped, headers kept
        pytest.param(
            werkzeug_response,
            HTTPStatus.OK,
            Headers([("X-Other", "val")]),
            (werkzeug_response, Headers([("X-Other", "val")])),
            id="werkzeug-response-status-matches-headers-different",
        ),
        # WerkzeugResponse — status differs, headers are the same object → headers dropped
        pytest.param(
            werkzeug_response,
            HTTPStatus.CREATED,
            shared_headers,
            (werkzeug_response, HTTPStatus.CREATED),
            id="werkzeug-response-status-differs-headers-same-object",
        ),
        # WerkzeugResponse — status differs, headers differ → both kept
        pytest.param(
            werkzeug_response,
            HTTPStatus.CREATED,
            Headers([("X-Other", "val")]),
            (werkzeug_response, HTTPStatus.CREATED, Headers([("X-Other", "val")])),
            id="werkzeug-response-status-differs-headers-different",
        ),
    ],
)
def test_pack_route_response(response_value, response_status, response_headers, expected):
    result = pack_route_response(response_value, response_status, response_headers)
    assert result == expected
