from collections.abc import Callable
from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise
from copy import deepcopy
from typing import Any

import pytest

from walker.config import Config, ConfigKey, ConfigValue, core
from walker.config.core import NoDefault

Empty = object()


@pytest.mark.parametrize(
    ("keys", "default", "converter", "value", "expectation"),
    [
        pytest.param(
            ["logging"],
            NoDefault,
            None,
            {"level": "DEBUG", "destination": "config.log"},
            does_not_raise(),
        ),
        pytest.param(
            ["logging", "level"],
            NoDefault,
            None,
            "DEBUG",
            does_not_raise(),
        ),
        pytest.param(
            ["logging", "destination"],
            NoDefault,
            None,
            "config.log",
            does_not_raise(),
        ),
        pytest.param(
            ["logging", "unknown"],
            NoDefault,
            None,
            Empty,
            pytest.raises(KeyError, match=r"Unknown value for keys 'logging.unknown'"),
        ),
        pytest.param(
            ["logging", "unknown"],
            "hola",
            None,
            "hola",
            does_not_raise(),
        ),
        pytest.param(
            ["null"],
            NoDefault,
            None,
            None,
            does_not_raise(),
        ),
        pytest.param(
            ["float"],
            NoDefault,
            None,
            4.2,
            does_not_raise(),
        ),
        pytest.param(
            ["float"],
            NoDefault,
            int,
            4,
            does_not_raise(),
        ),
        pytest.param(
            ["int"],
            NoDefault,
            None,
            29,
            does_not_raise(),
        ),
        pytest.param(
            ["int"],
            NoDefault,
            str,
            "29",
            does_not_raise(),
        ),
        pytest.param(
            ["mapping"],
            NoDefault,
            None,
            {"a": 5},
            does_not_raise(),
        ),
        pytest.param(
            ["mapping", "a"],
            NoDefault,
            None,
            5,
            does_not_raise(),
        ),
        pytest.param(
            ["array"],
            NoDefault,
            None,
            [1, "2", 3.0],
            does_not_raise(),
        ),
        pytest.param(
            ["no-se"],
            NoDefault,
            None,
            Empty,
            pytest.raises(KeyError, match=r"Unknown value for keys 'no-se'"),
        ),
        pytest.param(
            ["no-se"],
            "si señor",
            None,
            "si señor",
            does_not_raise(),
        ),
    ],
)
def test_get(
    config: Config,
    keys: list[ConfigKey],
    default: ConfigValue,
    converter: Callable[[ConfigValue], Any],
    value: ConfigValue,
    expectation: AbstractContextManager,
) -> None:
    with expectation:
        assert core.get(config, *keys, default=default, converter=converter) == value


@pytest.mark.parametrize(
    ("keys", "result"),
    [
        pytest.param(["logging"], True),
        pytest.param(["logging", "level"], True),
        pytest.param(["logging", "destination"], True),
        pytest.param(["logging", "unknown"], False),
        pytest.param(["null"], True),
        pytest.param(["float"], True),
        pytest.param(["int"], True),
        pytest.param(["mapping"], True),
        pytest.param(["mapping", "a"], True),
        pytest.param(["mapping", "bidule"], False),
        pytest.param(["array"], True),
        pytest.param(["no-se"], False),
        pytest.param(["no", "se"], False),
    ],
)
def test_has(
    config: Config,
    keys: list[ConfigKey],
    result: bool,
) -> None:
    assert core.has(config, *keys) == result


@pytest.mark.parametrize(
    ("keys", "value", "overwrite", "expectation"),
    [
        pytest.param(
            ["logging"],
            Empty,
            False,
            pytest.raises(
                KeyError, match=r"Value for keys 'logging' already exists in the given 'config'"
            ),
        ),
        pytest.param(
            ["logging"],
            "truc",
            True,
            does_not_raise(),
        ),
        pytest.param(
            ["logging", "bidule"],
            "truc",
            False,
            does_not_raise(),
        ),
        pytest.param(
            ["logging", "bidule"],
            "truc",
            True,
            does_not_raise(),
        ),
        pytest.param(
            ["logging", "level"],
            "INFO",
            False,
            pytest.raises(
                KeyError,
                match=r"Value for keys 'logging.level' already exists in the given 'config'",
            ),
        ),
        pytest.param(
            ["logging", "level"],
            "INFO",
            True,
            does_not_raise(),
        ),
        pytest.param(
            ["logging", "destination", "file"],
            "truc.log",
            False,
            pytest.raises(
                KeyError,
                match=r"Value for keys 'logging.destination' already exists in the given 'config'",
            ),
        ),
        pytest.param(
            ["logging", "destination", "file"],
            "truc.log",
            True,
            does_not_raise(),
        ),
        pytest.param(
            ["coucou"],
            1,
            False,
            does_not_raise(),
        ),
        pytest.param(
            ["coucou"],
            2,
            True,
            does_not_raise(),
        ),
        pytest.param(
            ["coucou", "bidule"],
            [1, 1, 2, 3, 5],
            False,
            does_not_raise(),
        ),
        pytest.param(
            ["coucou", "bidule"],
            [5, 3, 2, 1, 1],
            True,
            does_not_raise(),
        ),
    ],
)
def test_put(
    config: Config,
    keys: list[ConfigKey],
    value: ConfigValue,
    overwrite: bool,
    expectation: AbstractContextManager,
) -> None:
    old_config = deepcopy(config)
    with expectation:
        core.put(config, *keys, value=value, overwrite=overwrite)

    if isinstance(expectation, pytest.RaisesExc):
        assert config == old_config
    else:
        *keys, last_key = keys
        for key in keys:
            assert key in config

            config = config[key]

        assert config[last_key] == value


@pytest.mark.parametrize(
    ("keys", "value"),
    [
        pytest.param(["logging"], "truc"),
        pytest.param(["logging", "bidule"], "truc"),
        pytest.param(["logging", "level"], "INFO"),
        pytest.param(["logging", "destination", "file"], "truc.log"),
    ],
)
def test_replace(
    config: Config,
    keys: list[ConfigKey],
    value: ConfigValue,
) -> None:
    core.replace(config, *keys, value=value)

    *keys, last_key = keys
    for key in keys:
        assert key in config

        config = config[key]

    assert config[last_key] == value


@pytest.mark.parametrize(
    ("config", "source", "new_config"),
    [
        pytest.param({}, {"a": 1}, {"a": 1}),
        pytest.param({}, {"a": {"a.a": 2}}, {"a": {"a.a": 2}}),
        pytest.param({"a": 1}, {}, {"a": 1}),
        pytest.param({"a": 1}, {"b": 1}, {"a": 1, "b": 1}),
        pytest.param({"a": 1}, {"a": 2}, {"a": 2}),
        pytest.param({"a": {"a.a": 2}}, {"a": 1}, {"a": 1}),
        pytest.param({"a": 1, "b": 1}, {"a": {"a.a": 2}}, {"a": {"a.a": 2}, "b": 1}),
        pytest.param({"a": {"a.a": {"a.a.a": 3}}}, {"a": 1}, {"a": 1}),
        pytest.param({"a": {"a.a": {"a.a.a": 3}}}, {"a": {"a.a": [2, 2]}}, {"a": {"a.a": [2, 2]}}),
        pytest.param(
            {"a": {"a.a": {"a.a.a": 3}}}, {"a": {"a.a": {"a.a.a": 3}}}, {"a": {"a.a": {"a.a.a": 3}}}
        ),
        pytest.param(
            {"a": {"a.a": {"a.a.a": 3}, "a.b": 2}},
            {"a": {"a.a": {"a.a.a": 3}}},
            {"a": {"a.a": {"a.a.a": 3}, "a.b": 2}},
        ),
    ],
)
def test_update(config: Config, source: Config, new_config: Config) -> None:
    core.update(config, source)

    assert config == new_config
