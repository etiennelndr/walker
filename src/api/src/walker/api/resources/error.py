"""Error resource for API responses.

This module defines the :py:class:`Error` class, which represents an error response from the API.

:py:class:`Error` instances contain standardized error information including HTTP status codes,
human-readable messages, and internal error codes for debugging and error handling.
"""

from quart import Response
from werkzeug.datastructures import Headers

from ._base import APIResource


class Error(APIResource):
    """Representation of an API error response.

    This class encapsulates error information returned by the API, providing structured access to
    HTTP status codes, error messages, and internal error codes.
    """

    status: int
    """HTTP status code"""
    message: str
    """Message to describe the error"""
    code: str
    """Internal error code"""

    def as_response(
        self,
        *,
        status: int | None = None,
        headers: dict | Headers | None = None,
    ) -> Response:
        """Converts this error instance to a response.

        :param status: status code of the response. Defaults to :py:attr:`status` if not provided.
        :param headers: headers to attach to the response.
        """
        status = status or self.status
        return super().as_response(status=status, headers=headers)


__all__ = ["Error"]
