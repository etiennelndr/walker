"""Blueprint to collect training states."""

from http import HTTPStatus
from typing import Final

from quart import Blueprint, current_app

import walker.api.attrs.config as wac
import walker.config as wc
from walker.api import attrs, middlewares
from walker.api.training import TrainingStore
from walker.core.resources.state import State

states_bp: Final = Blueprint("states", __name__, url_prefix="/states")


@states_bp.before_app_serving
async def open_training_store() -> None:
    """Opens the storage of the collected training states.

    Runs automatically before serving starts.

    :raises RuntimeError: if no path is configured for the training states.
    """
    path = wc.app.get(wac.App.TRAINING, wac.Training.PATH)
    if path is None:
        raise RuntimeError("A path must be configured to collect training states")

    training_store = TrainingStore(path)
    await training_store.open()
    current_app.extensions[attrs.Extensions.TRAINING_STORE] = training_store


@states_bp.after_app_serving
async def close_training_store() -> None:
    """Closes the storage of the collected training states.

    Runs automatically after serving ends.
    """
    training_store: TrainingStore = current_app.extensions.pop(attrs.Extensions.TRAINING_STORE)
    await training_store.close()


@states_bp.post("")
@middlewares.request(
    middlewares.req.validate(data=State),
)
@middlewares.response(
    middlewares.res.validate(
        {
            HTTPStatus.CREATED: State,
        }
    ),
)
async def create_state(data: State) -> tuple[State, int]:
    """Saves a training state.

    :returns: the saved training state.
    """
    training_store: TrainingStore = current_app.extensions[attrs.Extensions.TRAINING_STORE]
    training_store.add(data)
    return data, HTTPStatus.CREATED


__all__ = ["states_bp"]
