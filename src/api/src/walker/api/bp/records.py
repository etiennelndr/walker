"""Blueprint to collect training records."""

from http import HTTPStatus
from typing import Final

from quart import Blueprint, current_app

import walker.api.attrs.config as wac
import walker.config as wc
from walker.api import attrs, middlewares
from walker.api.training import TrainingStore
from walker.core.resources.record import Record

records_bp: Final = Blueprint("records", __name__, url_prefix="/records")


@records_bp.before_app_serving
async def open_training_store() -> None:
    """Opens the storage of the collected training records.

    Runs automatically before serving starts.

    :raises RuntimeError: if no path is configured for the training records.
    """
    path = wc.app.get(wac.App.TRAINING, wac.Training.PATH)
    if path is None:
        raise RuntimeError("A path must be configured to collect training records")

    training_store = TrainingStore(path)
    await training_store.open()
    current_app.extensions[attrs.Extensions.TRAINING_STORE] = training_store


@records_bp.after_app_serving
async def close_training_store() -> None:
    """Closes the storage of the collected training records.

    Runs automatically after serving ends.
    """
    training_store: TrainingStore = current_app.extensions.pop(attrs.Extensions.TRAINING_STORE)
    await training_store.close()


@records_bp.post("")
@middlewares.request(
    middlewares.req.validate(data=Record),
)
@middlewares.response(
    middlewares.res.validate(
        {
            HTTPStatus.CREATED: Record,
        }
    ),
)
async def create_record(data: Record) -> tuple[Record, int]:
    """Saves a training record.

    :returns: the saved training record.
    """
    training_store: TrainingStore = current_app.extensions[attrs.Extensions.TRAINING_STORE]
    training_store.add(data)
    return data, HTTPStatus.CREATED


__all__ = ["records_bp"]
