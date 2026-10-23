import json
from typing import Any
from uuid import UUID

import pytest

from tests.data import OBSERVATION, PATROLLING_RECORD, RECORD, TRAINING_RECORD
from walker.core.resources import ResourceDecodingError
from walker.core.resources.observation import Observation
from walker.core.resources.record import Record
from walker.core.resources.vector import Vector3

TRAINING_FIELDS: dict[str, Any] = {
    "desired_velocity": Vector3(x=3.5, y=0.0, z=0.0),
    "target": Vector3(x=10.0, y=0.0, z=0.0),
}
PATROLLING_FIELDS: dict[str, Any] = {
    "contacts": 2,
    "walk": Vector3(x=0.0, y=0.0, z=3.5),
}


def make_record(**fields: Any) -> Record:
    return Record(
        session=UUID("1b4e28ba-2fa1-41d2-883f-0016d3cca427"),
        walker="Walker",
        scene="scene",
        frame=42,
        time=4.2,
        observation=Observation.decode(OBSERVATION),
        **fields,
    )


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(RECORD, make_record(), id="shared-fields"),
        pytest.param(TRAINING_RECORD, make_record(**TRAINING_FIELDS), id="training"),
        pytest.param(PATROLLING_RECORD, make_record(**PATROLLING_FIELDS), id="patrolling"),
        pytest.param(
            TRAINING_RECORD | PATROLLING_RECORD,
            make_record(**TRAINING_FIELDS, **PATROLLING_FIELDS),
            id="training-and-patrolling",
        ),
    ],
)
def test_decode(data: dict[str, Any], expected: Record) -> None:
    assert Record.decode(json.dumps(data)) == expected


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(RECORD, id="shared-fields"),
        pytest.param(TRAINING_RECORD, id="training"),
        pytest.param(PATROLLING_RECORD, id="patrolling"),
        pytest.param(TRAINING_RECORD | PATROLLING_RECORD, id="training-and-patrolling"),
    ],
)
def test_encode(data: dict[str, Any]) -> None:
    record = Record.decode(data)

    # Fields left empty are not encoded
    assert json.loads(record.encode()) == data


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({}, id="empty"),
        pytest.param(
            {key: value for key, value in RECORD.items() if key != "observation"},
            id="missing-field",
        ),
        pytest.param(RECORD | {"session": "session"}, id="session-format"),
        pytest.param(RECORD | {"contacts": "many"}, id="field-type"),
    ],
)
def test_decode_invalid(data: dict[str, Any]) -> None:
    with pytest.raises(ResourceDecodingError):
        Record.decode(json.dumps(data))
