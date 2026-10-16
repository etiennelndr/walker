import pytest

from walker.config import ConfigKey, utils


@pytest.mark.parametrize(
    ("text", "result"),
    [
        pytest.param("text", "text"),
        pytest.param("input_text", "inputtext"),
        pytest.param("input_Text", "input_Text"),
        pytest.param("input_text_super_long_snake_case", "inputtextsuperlongsnakecase"),
    ],
)
def test_snake_to_flat_case(text: str, result: str) -> None:
    assert utils.snake_to_flat_case(text) == result


@pytest.mark.parametrize(
    ("elements", "result"),
    [
        pytest.param([], []),
        pytest.param([1, [2, [3]], [[[[4]]], 5]], [1, 2, 3, 4, 5]),
        pytest.param([{"a": 1}], [{"a": 1}]),
        pytest.param(["coucou"], ["coucou"]),
    ],
)
def test_flatten(elements: utils.NestedIterable, result: list) -> None:
    assert list(utils.flatten(elements)) == result


@pytest.mark.parametrize(
    ("keys", "result"),
    [
        pytest.param(["a"], "a"),
        pytest.param(["a", "b", "c"], "a.b.c"),
        pytest.param(["a", "b", ["c", "d"]], "a.b.c.d"),
        pytest.param([["a", [["b"]]], [[["c"], "d"], "e"], "f"], "a.b.c.d.e.f"),
    ],
)
def test_concatenate_keys(keys: utils.NestedIterable[ConfigKey], result: str) -> None:
    assert utils.concatenate_keys(*keys) == result
