"""Middleware components for HTTP response processing."""

from collections.abc import MutableMapping
from functools import wraps
from http import HTTPStatus

from loguru import logger
from quart_schema import ResponseSchemaValidationError, validate_response

from walker.api.http.error import HTTPError
from walker.api.resources import APIResource
from walker.api.resources.error import Error
from walker.api.typing import Route, RouteResponse, RouteResponseValue

from ._base import Middleware


def response(*middlewares: Middleware) -> Middleware:
    """Composes multiple response middlewares into a single decorator.

    :param middlewares: middleware callables to compose.
    :returns: a decorator that applies all middlewares to a function.
    """

    def _decorator(route: Route) -> Route:
        for middleware in middlewares:
            route = middleware(route)
        return route

    return _decorator


def validate(
    responses: MutableMapping[
        int,
        type[RouteResponseValue]
        | tuple[
            type[RouteResponseValue],
            type[APIResource],
        ],
    ],
) -> Middleware:
    """Validates response content against types for specific status codes.

    Applies validation to responses based on their HTTP status code. Each status can have either a
    single response type or a tuple of `(response type, headers type)`.

    By default, error schemas are automatically added for the following HTTP status codes:

    * 400: :py:class:`~walker.api.resources.error.Error`;
    * 500: :py:class:`~walker.api.resources.error.Error`.

    :param responses: mapping of HTTP status codes to their validation types. Values can be a
        single response type or a tuple of `(response type, headers type)`.
    :returns: a middleware decorator that validates responses for the specified status codes.
    """

    def _decorator[**P, T: RouteResponseValue](route: Route[P, T]) -> Route[P, T]:
        responses.setdefault(HTTPStatus.BAD_REQUEST, Error)
        responses.setdefault(HTTPStatus.INTERNAL_SERVER_ERROR, Error)

        for status, models in responses.items():
            if isinstance(models, tuple):
                middleware = validate_response(models[0], status, models[1])
            else:
                middleware = validate_response(models, status)

            route = middleware(route)

        @wraps(route)
        async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse[T]:
            try:
                return await route(*args, **kwargs)
            except ResponseSchemaValidationError:
                logger.exception("An error occurred while validating a response")
                HTTPError.INTERNAL_ERROR.abort()

        return _wrapper

    return _decorator


__all__ = ["response", "validate"]
