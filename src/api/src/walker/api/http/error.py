"""Helpers to create and raise HTTP errors."""

from __future__ import annotations

from collections.abc import Iterator
from enum import Enum
from http import HTTPStatus
from typing import Any, NoReturn

from quart import Response, current_app
from werkzeug.datastructures import Headers

from walker.api.resources.error import Error


def generate_http_error_codes() -> Iterator[str]:
    """Yields unique HTTP error codes indefinitely.

    :Example:

    >>> gen = generate_http_error_codes()
    >>> next(gen)
    'WALKER-API-0001'
    >>> next(gen)
    'WALKER-API-0002'
    """
    code = 1
    while True:
        yield f"WALKER-API-{code:04d}"
        code += 1


http_code_generator = generate_http_error_codes()
http_code = lambda: next(http_code_generator)  # noqa: E731


class _HTTPError(Enum):
    """Base class for the enumeration of HTTP errors."""

    value: Error  # type: ignore[misc]

    def abort(
        self,
        *,
        message: str | None = None,
        headers: dict | Headers | None = None,
    ) -> NoReturn:
        """Raises an HTTP error.

        :param message: overrides the default error message.
        :param headers: HTTP headers to attach to the error.
        """
        value = self.value
        if message is not None:
            value = value.replace(message=message)

        response = value.as_response(headers=headers)
        current_app.aborter(response)

    def as_dict(self) -> dict[str, Any]:
        """Converts this HTTP error instance to a :py:class:`dict`.

        :returns: a :py:class:`dict` of field names to their values.
        """
        return self.value.as_dict()

    def as_response(
        self,
        *,
        headers: dict | Headers | None = None,
    ) -> Response:
        """Converts this HTTP error instance to a response.

        :param headers: headers to attach to the response.
        """
        return self.value.as_response(headers=headers)

    @property
    def status(self) -> int:
        """HTTP error status."""
        return self.value.status

    @property
    def message(self) -> str:
        """HTTP error message."""
        return self.value.message

    @property
    def code(self) -> str:
        """HTTP error code."""
        return self.value.code


class HTTPError(_HTTPError):
    """Preconfigured HTTP errors that may be raised during the processing of HTTP messages.

    This enumeration provides a centralized collection of internal HTTP errors with predefined
    status codes, messages, and error codes. Each enum member can be raised as an HTTP response
    using the :py:meth:`abort` method.
    """

    INTERNAL_ERROR = Error(
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        message="An internal error has occurred",
        code=http_code(),
    )

    INVALID_REQUEST = Error(
        status=HTTPStatus.BAD_REQUEST,
        message="Incoming HTTP request is malformed or invalid",
        code=http_code(),
    )
    INVALID_HEADERS = Error(
        status=HTTPStatus.BAD_REQUEST,
        message="One or more HTTP headers are missing, malformed, or contain invalid values",
        code=http_code(),
    )
    INVALID_QUERYSTRING = Error(
        status=HTTPStatus.BAD_REQUEST,
        message="One or more query parameters are missing, malformed, or contain invalid values",
        code=http_code(),
    )
    INVALID_JSON = Error(
        status=HTTPStatus.BAD_REQUEST,
        message="One or more JSON parameters are missing, malformed, or contain invalid values",
        code=http_code(),
    )
    INVALID_FORM = Error(
        status=HTTPStatus.BAD_REQUEST,
        message="One or more form parameters are missing, malformed, or contain invalid values",
        code=http_code(),
    )
    INVALID_FORM_MULTIPART = Error(
        status=HTTPStatus.BAD_REQUEST,
        message="One or more form-multipart parameters are missing, malformed, or contain invalid"
        " values",
        code=http_code(),
    )


__all__ = ["HTTPError"]
