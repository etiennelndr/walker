"""Helpers to work with HTTP responses."""

from functools import singledispatch

from quart import Response, current_app
from werkzeug.datastructures import Headers

from walker.api.resources.error import Error
from walker.core.resources import Resource


@singledispatch
def make_resource_response(
    resource: Resource,
    *,
    status: int | None = None,
    headers: dict | Headers | None = None,
    response_class: type[Response] | None = None,
) -> Response:
    """Makes a JSON response from a resource.

    :param resource: resource to put in the body of the response.
    :param status: status code of the response.
    :param headers: headers to attach to the response.
    :param response_class: class of the response. Defaults to the response class of the current
        application, or to :py:class:`quart.Response` outside an application context.
    :returns: a response whose body is the resource encoded in JSON.
    """
    if response_class is None:
        try:
            response_class = current_app.response_class
        except RuntimeError:
            response_class = Response

    return response_class(
        resource.encode(),
        status=status,
        headers=headers,
        mimetype="application/json",
    )


@make_resource_response.register
def _(
    resource: Error,
    *,
    status: int | None = None,
    headers: dict | Headers | None = None,
    response_class: type[Response] | None = None,
) -> Response:
    """Makes a JSON response from an error.

    :param resource: error to put in the body of the response.
    :param status: status code of the response. Defaults to the status of the error.
    :param headers: headers to attach to the response.
    :param response_class: class of the response. Defaults to the response class of the current
        application, or to :py:class:`quart.Response` outside an application context.
    :returns: a response whose body is the error encoded in JSON.
    """
    status = status or resource.status
    return make_resource_response.dispatch(Resource)(
        resource,
        status=status,
        headers=headers,
        response_class=response_class,
    )


__all__ = ["make_resource_response"]
