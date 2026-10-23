"""Blueprint to generate the movements of walkers."""

from http import HTTPStatus
from typing import Final

from loguru import logger
from quart import Blueprint

from walker.api import middlewares
from walker.api.websocket import websocket
from walker.core.resources.observation import Observation
from walker.core.resources.vector import Vector3

walks_bp: Final = Blueprint("walks", __name__, url_prefix="/walks")


@walks_bp.post("")
@middlewares.request(
    middlewares.req.validate(data=Observation),
)
@middlewares.response(
    middlewares.res.validate(
        {
            HTTPStatus.OK: Vector3,
        }
    ),
)
async def generate_walk(data: Observation) -> Vector3:
    """Generates the movement a walker has to perform from its observation."""
    logger.debug(data.as_dict())
    return Vector3(x=0, y=0, z=0)


@walks_bp.websocket("")
async def generate_walks() -> None:
    """Generates the movement a walker has to perform for each observation it sends."""
    while True:
        observation = await websocket.receive_as(Observation)
        logger.debug(observation.as_dict())
        await websocket.send_as({"x": 0, "y": 0, "z": 0}, Vector3)


__all__ = ["walks_bp"]
