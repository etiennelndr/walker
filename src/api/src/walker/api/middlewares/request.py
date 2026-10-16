"""Middleware components for HTTP request processing."""

from functools import wraps

from loguru import logger
from quart_schema import DataSource, validate_headers, validate_querystring
from quart_schema import validate_request as validate_data
from quart_schema.validation import (
    QuerystringValidationError,
    RequestHeadersValidationError,
    RequestSchemaValidationError,
    validate_response,
)

from walker.api.http.error import HTTPError
from walker.api.resources import APIResource
from walker.api.typing import Route, RouteResponse, RouteResponseValue

from ..resources.error import Error
from ._base import Middleware


def request(*middlewares: Middleware) -> Middleware:
    """Composes multiple request middlewares into a single decorator.

    Middlewares are applied in reverse order. Thus, the first middleware in the arguments list will
    be the outermost wrapper, and so the first called.

    :param middlewares: middleware callables to compose.
    :returns: a decorator that applies all middlewares to a function.
    """

    def _decorator(route: Route) -> Route:
        for middleware in reversed(middlewares):
            route = middleware(route)
        return route

    return _decorator


def validate(
    *,
    headers: type[APIResource] | None = None,
    querystring: type[APIResource] | None = None,
    data: type[APIResource] | None = None,
    data_source: DataSource = DataSource.JSON,
) -> Middleware:
    """Validates requests against defined schemas.

    Combines validation of headers, querystring parameters, and request body into a single
    middleware decorator. Validations are applied in the order: headers, querystring, then data.

    :param headers: schema class for validating request headers.
    :param querystring: schema class for validating querystring parameters.
    :param data: schema class for validating request data.
    :param data_source: source format of the request data (default: JSON).
    :returns: a middleware decorator that validates the specified request components.
    """

    def _decorator[**P, T: RouteResponseValue](route: Route[P, T]) -> Route[P, T]:
        if headers is not None:
            route = validate_headers(headers)(route)
            route = validate_response(Error, HTTPError.INVALID_HEADERS.status)(route)
        if querystring is not None:
            route = validate_querystring(querystring)(route)
            route = validate_response(Error, HTTPError.INVALID_QUERYSTRING.status)(route)
        if data is not None:
            route = validate_data(data, source=data_source)(route)
            route = validate_response(Error, HTTPError.INVALID_JSON.status)(route)
            route = validate_response(Error, HTTPError.INVALID_FORM.status)(route)
            route = validate_response(Error, HTTPError.INVALID_FORM_MULTIPART.status)(route)
            route = validate_response(Error, HTTPError.INVALID_REQUEST.status)(route)

        @wraps(route)
        async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse[T]:
            try:
                return await route(*args, **kwargs)
            except RequestHeadersValidationError:
                HTTPError.INVALID_HEADERS.abort()
            except QuerystringValidationError:
                HTTPError.INVALID_QUERYSTRING.abort()
            except RequestSchemaValidationError:
                match data_source:
                    case DataSource.JSON:
                        HTTPError.INVALID_JSON.abort()
                    case DataSource.FORM:
                        HTTPError.INVALID_FORM.abort()
                    case DataSource.FORM_MULTIPART:
                        HTTPError.INVALID_FORM_MULTIPART.abort()
                    case _:
                        logger.error(
                            "Unable to raise appropriate HTTP error from unknown data source"
                            f" '{getattr(data_source, 'name', data_source)}'"
                        )
                        HTTPError.INVALID_REQUEST.abort()

        return _wrapper

    return _decorator


__all__ = ["request", "validate"]
