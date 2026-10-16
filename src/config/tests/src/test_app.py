import os
from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from tests.data import CONFIG_FOLDER
from walker.config import Config, ConfigKey, ConfigValue, app, templates
from walker.config.core import NoDefault

Empty = object()


@pytest.fixture
def config(config: Config) -> Config:
    app._APP_CONFIG = config
    return config


def test_configure() -> None:
    app_config = {}

    os.environ["TESTDIR"] = str(CONFIG_FOLDER)
    os.environ["TEST_ENV"] = "test"
    os.environ["TEST_LOGGING__DESTINATION"] = "config.log"
    os.environ["TEST_MAPPING"] = "{'a': 5}"
    os.environ["TEST_TRUC"] = "[1, 1, 2, 3, 5]"

    app.configure(
        app_config,
        app_name="test",
        app_template={
            "logging": {"level": str, "destination": templates.Path()},
            "null": None,
            "float": float,
            "int": int,
            "mapping": dict,
            "array": list,
        },
    )

    assert "logging" in app_config
    assert "level" in app_config["logging"]
    assert app_config["logging"]["level"] == "DEBUG"
    assert "destination" in app_config["logging"]
    assert app_config["logging"]["destination"] == Path("config.log")
    assert "null" in app_config
    assert app_config["null"] is None
    assert "float" in app_config
    assert app_config["float"] == 4.2
    assert "int" in app_config
    assert app_config["int"] == 29
    assert "mapping" in app_config
    assert "a" in app_config["mapping"]
    assert app_config["mapping"]["a"] == 5
    assert "array" in app_config
    assert app_config["array"] == [1, "2", 3.0]
    assert "truc" in app_config
    assert app_config["truc"] == [1, 1, 2, 3, 5]


@pytest.mark.usefixtures("config")
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
    keys: Sequence[ConfigKey],
    default: ConfigValue,
    converter: Callable[[ConfigValue], Any],
    value: ConfigValue,
    expectation: AbstractContextManager,
) -> None:
    with expectation:
        assert app.get(*keys, default=default, converter=converter) == value


@pytest.mark.usefixtures("config")
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
def test_has(keys: Sequence[ConfigKey], result: bool) -> None:
    assert app.has(*keys) == result


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
        app.put(*keys, value=value, overwrite=overwrite)

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
    app.replace(*keys, value=value)

    *keys, last_key = keys
    for key in keys:
        assert key in config

        config = config[key]

    assert config[last_key] == value


@pytest.mark.parametrize(
    ("config", "source", "new_config"),
    [
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
    app._APP_CONFIG = config

    app.update(source)

    assert config == new_config
