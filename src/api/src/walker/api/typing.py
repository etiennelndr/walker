"""Internal typing definitions."""

from collections.abc import Awaitable, Callable, Iterator, Mapping
from typing import TYPE_CHECKING, Any

from quart import Response
from quart.typing import StatusCode
from quart.wrappers import Websocket as QuartWebsocket
from quart_schema.mixins import WebsocketMixin
from werkzeug import Response as WerkzeugResponse
from werkzeug.datastructures import Headers

from walker.api.resources import APIResource

type RouteResponseValue = (
    Response
    | WerkzeugResponse
    | APIResource
    | bytes
    | str
    | Mapping[str, Any]
    | list[Any]
    | Iterator[bytes]
    | Iterator[str]
)
type RouteResponse[T: RouteResponseValue] = (
    T | tuple[T, Headers] | tuple[T, StatusCode] | tuple[T, StatusCode, Headers]
)
type Route[**P, T: RouteResponseValue] = Callable[P, Awaitable[RouteResponse[T]]]


class Websocket(WebsocketMixin, QuartWebsocket):
    """Websocket class of the application, as extended by QuartSchema.

    QuartSchema replaces the websocket class of the application with a subclass providing the
    `receive_as` and `send_as` methods, which the type of the :py:data:`quart.websocket` proxy
    doesn't know about: cast this proxy to this class to use them.
    """

    if TYPE_CHECKING:
        # QuartSchema types the loaded model as the union of all supported model types. These
        # signatures bind it to the requested model class instead
        async def receive_as[T](self, model_class: type[T]) -> T: ...

        async def send_as[T](self, value: Any, model_class: type[T]) -> None: ...


__all__ = ["Route", "RouteResponse", "RouteResponseValue", "Websocket"]
