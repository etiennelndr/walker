"""Utilities for working with REST API routes."""

from loguru import logger
from quart import Response as QuartResponse
from quart.typing import StatusCode
from werkzeug import Response as WerkzeugResponse
from werkzeug.datastructures import Headers

from .http.error import HTTPError
from .typing import RouteResponse, RouteResponseValue


def unpack_route_response[T: RouteResponseValue](
    response: RouteResponse[T],
) -> tuple[T, StatusCode | None, Headers | None]:
    """Unpacks a route return response into its components.

    Accepts any of the four valid route return forms: ``(value, status, headers)``, ``(value,
    status)``, ``(value, headers)``, or ``value`` alone.

    :param response: the response returned by a route handler.
    :returns: a 3-tuple of ``(value, status, headers)``, where ``status`` and ``headers`` may be
        ``None`` if not provided by the route.
    :raises HTTPError: if the response is a tuple with an invalid number of elements.
    """
    if not isinstance(response, tuple):
        return response, None, None

    response_value: T
    response_status: StatusCode | None = None
    response_headers: Headers | None = None
    if len(response) == 3:  # noqa: PLR2004
        response_value, response_status, response_headers = response
    elif len(response) == 2:  # noqa: PLR2004
        response_value, status_or_headers = response
        if isinstance(status_or_headers, StatusCode):
            response_status = status_or_headers
        else:
            response_headers = status_or_headers
    else:
        logger.error(
            # This error message is adapted from `flask.app.Flask:make_response`
            "The route did not return a valid response tuple. The tuple must have the form"
            " (body, status, headers), (body, status), or (body, headers)."
        )
        HTTPError.INTERNAL_ERROR.abort()

    return response_value, response_status, response_headers


def pack_route_response[T: RouteResponseValue](
    response_value: T,
    response_status: StatusCode | None = None,
    response_headers: Headers | None = None,
) -> RouteResponse[T]:
    """Packs the response components into a valid route response format.

    The provided value, status code, and headers are evaluated and combined into either a single
    value or a tuple, omitting any unprovided elements.  For :py:class:`quart.Response` and
    :py:class:`werkzeug.wrappers.Response` instances, any status code or headers already embedded
    in the response object are omitted to avoid duplication.

    :Example:

    >>> pack_route_response({"x": 0.0}, None, Headers())
    ({'x': 0.0}, Headers())

    :param response_value: the data be returned by the route.
    :param response_status: the optional HTTP status code.
    :param response_headers: the optional dictionary of HTTP headers.
    :returns: a correctly formatted route response.
    """
    if isinstance(response_value, QuartResponse | WerkzeugResponse):
        # Drops the status code if it matches the one already set on the response
        if response_value.status_code == response_status:
            response_status = None
        # Drops the headers if they are the same object as the ones already set on the response
        if response_value.headers is response_headers:
            response_headers = None

    match response_status, response_headers:
        case None, None:
            return response_value
        case None, Headers():
            return response_value, response_headers
        case StatusCode(), None:
            return response_value, response_status
        case _:
            return response_value, response_status, response_headers  # type: ignore[return-value]


__all__ = [
    "unpack_route_response",
    "pack_route_response",
]
