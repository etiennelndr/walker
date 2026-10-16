"""Helpers to read and write nested configuration items."""

import functools
import operator
from collections.abc import Callable, Mapping, MutableMapping
from typing import Any, Final, cast, overload

from .utils import concatenate_keys

type ConfigKey = str
type ConfigValue = Any
type Config = MutableMapping[ConfigKey, ConfigValue]

NoDefault: Final = object()
"""Sentinel to tell apart a missing default value from a ``None`` one"""


@overload
def get[T](
    config: Mapping[ConfigKey, ConfigValue],
    *keys: ConfigKey,
    default: ConfigValue = ...,
    converter: Callable[[ConfigValue], T],
) -> T: ...


@overload
def get(
    config: Mapping[ConfigKey, ConfigValue],
    *keys: ConfigKey,
    default: ConfigValue = NoDefault,
    converter: None = None,
) -> ConfigValue: ...


def get[T](
    config: Mapping[ConfigKey, ConfigValue],
    *keys: ConfigKey,
    default: ConfigValue = NoDefault,
    converter: Callable[[ConfigValue], T] | None = None,
) -> ConfigValue | T:
    """Retrieves the value of a configuration item.

    :param config: configuration to read.
    :param keys: path of the item, from the outermost key to the innermost one.
    :param default: value returned if the item does not exist.
    :param converter: optional function to convert the returned value.
    :returns: the value of the item.
    :raises KeyError: if the item does not exist and no default value is provided.
    """
    try:
        value = cast(ConfigValue, functools.reduce(operator.getitem, keys, config))
    except (KeyError, TypeError) as err:
        if default is NoDefault:
            raise KeyError(f"Unknown value for keys '{concatenate_keys(keys)}'") from err

        value = default

    if converter is not None:
        value = converter(value)

    return value


def has(config: Mapping[ConfigKey, ConfigValue], *keys: ConfigKey) -> bool:
    """Checks whether a configuration has an item.

    :param config: configuration to read.
    :param keys: path of the item, from the outermost key to the innermost one.
    """
    try:
        functools.reduce(operator.getitem, keys, config)
    except KeyError, TypeError:
        return False

    return True


DUPLICATE_ERROR_MSG: Final = "Value for keys '{keys}' already exists in the given 'config'"


def put[C: Config](config: C, *keys: ConfigKey, value: ConfigValue, overwrite: bool = False) -> C:
    """Sets the value of a configuration item, creating its parents if they do not exist.

    Update is performed in-place.

    :param config: configuration to update.
    :param keys: path of the item, from the outermost key to the innermost one.
    :param value: value of the item.
    :param overwrite: whether an existing value may be overwritten. Disabled by default.
    :returns: the updated configuration.
    :raises KeyError: if the item, or one of its parents, already has a value and `overwrite` is
        disabled.
    """
    *parent_keys, last_key = keys

    parent_config: Config = config
    for key_idx, key in enumerate(parent_keys):
        if key not in parent_config:
            parent_config[key] = {}
        elif not isinstance(parent_config[key], MutableMapping):
            if not overwrite:
                raise KeyError(
                    DUPLICATE_ERROR_MSG.format(keys=concatenate_keys(parent_keys[: key_idx + 1]))
                )

            parent_config[key] = {}

        parent_config = parent_config[key]

    if last_key in parent_config and not overwrite:
        raise KeyError(DUPLICATE_ERROR_MSG.format(keys=concatenate_keys(keys)))

    parent_config[last_key] = value
    return config


def replace[C: Config](config: C, *keys: ConfigKey, value: ConfigValue) -> C:
    """Sets the value of a configuration item, overwriting the existing one if any.

    Update is performed in-place.

    :param config: configuration to update.
    :param keys: path of the item, from the outermost key to the innermost one.
    :param value: new value of the item.
    :returns: the updated configuration.
    """
    return put(config, *keys, value=value, overwrite=True)


def update[C: Config](config: C, source: Mapping[ConfigKey, ConfigValue]) -> C:
    """Deeply updates a configuration.

    Update is performed in-place.

    :param config: configuration to update.
    :param source: items to merge into the configuration.
    :returns: the updated configuration.
    """
    # If the input config is empty, directly call 'dict.update' for a faster update
    if not config:
        config.update(source)
        return config

    items: list[tuple[list[ConfigKey], ConfigValue]] = [
        ([key], value) for key, value in source.items()
    ]
    for keys, value in items:
        if isinstance(value, Mapping) and value:
            items.extend(([*keys, k], v) for k, v in value.items())
        else:
            replace(config, *keys, value=value)

    return config


__all__ = [
    "NoDefault",
    "Config",
    "ConfigKey",
    "ConfigValue",
    "get",
    "has",
    "put",
    "replace",
    "update",
]
