from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import Any

import confuse
import pytest

from walker.config import templates


@pytest.fixture
def view() -> confuse.ConfigView:
    return confuse.RootView({"file": "coucou.txt", "number": 1})


@pytest.mark.parametrize(
    ("default", "expectation"),
    [
        pytest.param("test.log", does_not_raise()),
        pytest.param(Path("test.log"), does_not_raise()),
        pytest.param(None, does_not_raise()),
        pytest.param(confuse.REQUIRED, does_not_raise()),
        pytest.param(
            29,
            pytest.raises(
                ValueError,
                match=r"If provided, 'default' must be a valid path or 'None', got '29'",
            ),
        ),
    ],
)
def test_instantiate(
    default: Any,
    expectation: AbstractContextManager,
) -> None:
    with expectation:
        template = templates.Path(default)

        if default in [None, confuse.REQUIRED]:
            assert template.default == default
        else:
            assert isinstance(template.default, Path)
            assert template.default == Path(default)


@pytest.mark.parametrize(
    ("value", "expectation"),
    [
        pytest.param("file.log", does_not_raise()),
        pytest.param("folder/file.log", does_not_raise()),
        pytest.param("folder", does_not_raise()),
        pytest.param(Path("file.log"), does_not_raise()),
        pytest.param(Path("folder/file.log"), does_not_raise()),
        pytest.param(Path("folder"), does_not_raise()),
        pytest.param(29, pytest.raises(confuse.ConfigTypeError)),
    ],
)
def test_convert(
    view: confuse.ConfigView,
    value: Any,
    expectation: AbstractContextManager,
) -> None:
    with expectation:
        converted_value = templates.Path().convert(value, view)

        assert isinstance(converted_value, Path)
        assert converted_value == Path(value)
