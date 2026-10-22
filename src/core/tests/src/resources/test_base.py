from collections.abc import Mapping
from typing import Any

import pytest

from walker.core.resources import Resource


class Data(Resource):
    a: str
    b: int


def test_replace() -> None:
    data = Data(a="coucou", b=1)

    new_data = data.replace()

    assert new_data is not data
    assert isinstance(new_data, Data)
    assert new_data == data

    new_data = data.replace(a="bonjour")

    assert data.a == "coucou"
    assert new_data is not data
    assert isinstance(new_data, Data)
    assert new_data.a == "bonjour"


def test_as_dict() -> None:
    data = Data(a="coucou", b=1)
    data_dict = data.as_dict()

    assert isinstance(data_dict, dict)
    assert set(data_dict.keys()) == {"a", "b"}
    assert data_dict["a"] == "coucou"
    assert data_dict["b"] == 1


@pytest.mark.parametrize(
    ("exclude", "kwargs", "expected"),
    [
        pytest.param(set(), {}, {}, id="all_unset"),
        pytest.param(set(), {"a": "bonjour", "b": 42}, {"a": "bonjour", "b": 42}, id="all_set"),
        pytest.param(set(), {"b": None}, {"b": None}, id="explicit_none"),
        pytest.param({"a"}, {}, {}, id="excluded_field_all_unset"),
        pytest.param({"a"}, {"b": 42}, {"b": 42}, id="excluded_field_some_set"),
        pytest.param({"a"}, {"b": None}, {"b": None}, id="excluded_field_explicit_none"),
    ],
)
def test_asdict_exclude_unset(
    exclude: set[str], kwargs: dict[str, Any], expected: dict[str, Any]
) -> None:
    """Test that `as_dict` returns only fields that are not UNSET."""
    patch = Data.partial(exclude=exclude)
    instance = patch(**kwargs)
    assert instance.as_dict() == expected


def test_encode() -> None:
    data = Data(a="coucou", b=1)
    data_encoded = data.encode()

    assert isinstance(data_encoded, bytes)
    assert data_encoded == b'{"a":"coucou","b":1}'


@pytest.mark.parametrize(
    ("data_encoded",),
    [
        pytest.param(b'{"a":"coucou","b":1}', id="bytes"),
        pytest.param('{"a":"coucou","b":1}', id="str"),
        pytest.param({"a": "coucou", "b": 1}, id="dict"),
    ],
)
def test_decode(data_encoded: bytes | str | Mapping[str, Any]) -> None:
    data = Data.decode(data_encoded)

    assert isinstance(data, Data)
    assert data.a == "coucou"
    assert data.b == 1
