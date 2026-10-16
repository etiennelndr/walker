from collections.abc import Mapping
from typing import Any

import pytest

from walker.api.resources import APIResource


class Resource(APIResource):
    a: str
    b: int


def test_replace() -> None:
    resource = Resource(a="coucou", b=1)

    new_resource = resource.replace()

    assert new_resource is not resource
    assert isinstance(new_resource, Resource)
    assert new_resource == resource

    new_resource = resource.replace(a="bonjour")

    assert resource.a == "coucou"
    assert new_resource is not resource
    assert isinstance(new_resource, Resource)
    assert new_resource.a == "bonjour"


def test_as_dict() -> None:
    resource = Resource(a="coucou", b=1)
    resource_dict = resource.as_dict()

    assert isinstance(resource_dict, dict)
    assert set(resource_dict.keys()) == {"a", "b"}
    assert resource_dict["a"] == "coucou"
    assert resource_dict["b"] == 1


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
    patch = Resource.partial(exclude=exclude)
    instance = patch(**kwargs)
    assert instance.as_dict() == expected


def test_encode() -> None:
    resource = Resource(a="coucou", b=1)
    resource_encoded = resource.encode()

    assert isinstance(resource_encoded, bytes)
    assert resource_encoded == b'{"a":"coucou","b":1}'


@pytest.mark.parametrize(
    ("resource_encoded",),
    [
        pytest.param(b'{"a":"coucou","b":1}', id="bytes"),
        pytest.param('{"a":"coucou","b":1}', id="str"),
        pytest.param({"a": "coucou", "b": 1}, id="dict"),
    ],
)
def test_decode(resource_encoded: bytes | str | Mapping[str, Any]) -> None:
    resource = Resource.decode(resource_encoded)

    assert isinstance(resource, Resource)
    assert resource.a == "coucou"
    assert resource.b == 1
