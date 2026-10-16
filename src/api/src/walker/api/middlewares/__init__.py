"""Middleware components for HTTP request and response processing.

Middlewares are callable wrappers that intercept and process requests or responses, allowing
cross-cutting concerns like logging or data transformation to be applied consistently across the
application.
"""

from . import request as req
from . import response as res
from ._base import Middleware
from .request import request
from .response import response

__all__ = ["Middleware", "req", "request", "res", "response"]
