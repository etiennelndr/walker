"""Error resource for API responses.

This module defines the :py:class:`Error` class, which represents an error response from the API.

:py:class:`Error` instances contain standardized error information including HTTP status codes,
human-readable messages, and internal error codes for debugging and error handling.
"""

from walker.core.resources import Resource


class Error(Resource):
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


__all__ = ["Error"]
