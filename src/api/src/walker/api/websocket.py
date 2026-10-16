"""Proxy to the current websocket, typed with the methods added by QuartSchema."""

from typing import Final, cast

import quart

from walker.api.typing import Websocket

websocket: Final = cast(Websocket, quart.websocket)

__all__ = ["websocket"]
