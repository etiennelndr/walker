"""Management of runtime application errors."""

from loguru import logger
from werkzeug.exceptions import HTTPException
from werkzeug.sansio.response import Response as HTTPResponse

from walker.api.http.error import HTTPError


async def handle_app_error(
    error: HTTPException | Exception,
) -> HTTPResponse:
    """Global application error handler for the application.

    This function is registered as the catch-all error handler. It inspects the incoming exception
    and determines whether it is an :py:class:`HTTPException`. If so, it returns the exception’s own
    HTTP response. Otherwise, it constructs a standardized internal server error payload, and
    returns it with a 500 status code.

    :Example:

    >>> from quart import Quart
    >>> app = Quart(__name__)
    >>> app.register_error_handler(Exception, handle_app_error)

    :param error: the exception raised during request processing.
    :returns: the response generated from an :py:class:`HTTPException` or a JSON error response
        with the HTTP status code ``500`` when handling unexpected exceptions.
    """
    if isinstance(error, HTTPException):
        return error.get_response()

    logger.exception("An internal error occurred")
    http_error = HTTPError.INTERNAL_ERROR
    http_response = http_error.as_response()
    http_response.status = http_error.status
    return http_response


__all__ = ["handle_app_error"]
