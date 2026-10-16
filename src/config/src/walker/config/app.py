"""Helpers to load and access the configuration of an application."""

import os
from collections.abc import Callable, Mapping
from typing import Any

from confuse import Configuration, EnvSource

from . import core
from .core import Config, ConfigKey, ConfigValue, NoDefault
from .utils import snake_to_flat_case

type ConfigTemplate = Mapping[str, Any]

_APP_CONFIG: Config = {}
"""Configuration of the current application, set by :py:func:`configure`"""


def configure(app_config: Config, app_name: str, app_template: ConfigTemplate) -> None:
    """Loads the configuration of an application and merges it into `app_config`.

    For an application named ``WALKER_API``, the configuration is read from:

    * the ``config.yaml`` file of the folder set in ``WALKERAPIDIR`` (underscores are removed from
      the application name), under the section of the environment set in ``WALKER_API_ENV``;
    * the environment variables prefixed with ``WALKER_API_``, which take precedence over the
      file. ``__`` separates nested keys (e.g. ``WALKER_API_ASGI__PORT``).

    The items described in `app_template` are validated against it. The other ones are kept as
    they are. Update of `app_config` is performed in-place.

    :param app_config: configuration to update.
    :param app_name: name of the application, in upper snake case. It is converted to upper case if
        it is not.
    :param app_template: Confuse template the configuration must comply with.
    :raises KeyError: if the environment variable that sets the application environment does not
        exist.
    :raises confuse.ConfigError: if the configuration does not comply with `app_template`.
    """
    global _APP_CONFIG  # noqa: PLW0603

    app_name = app_name.upper()
    app_env = os.environ[f"{app_name}_ENV"]

    config_handler = Configuration(appname=snake_to_flat_case(app_name.lower()), read=False)
    # Prepare to overload configuration fields from environment variables
    config_handler.add(
        EnvSource(
            f"{app_name}_",
            loader=config_handler.loader,
            parse_yaml_docs=True,
            handle_lists=False,
        )
    )
    # Parse environment variables without applying any template. This ensures that even values not
    # explicitly defined in the configuration template are loaded and available.
    config_from_env = config_handler.get()
    # Remove all sources to ensure environment variables are not parsed twice
    config_handler.clear()
    # Then, add the configuration extracted from the environment variables as a raw source
    config_handler.add({app_env: config_from_env})

    config_handler.read()

    config = config_handler[app_env].flatten()
    # Validate default parameters. Those parameters must respect specific types to avoid
    # configuration errors.
    default_config = config_handler[app_env].get(app_template)
    core.update(config, default_config)

    # Finally, save the loaded configuration in the application configuration
    core.update(app_config, config)
    # Keep a reference of the application configuration in a global variable
    _APP_CONFIG = app_config


def get[T](
    *keys: ConfigKey,
    default: ConfigValue = NoDefault,
    converter: Callable[[ConfigValue], T] | None = None,
) -> ConfigValue | T:
    """Retrieves the value of an item from the configuration of the current application.

    :param keys: path of the item, from the outermost key to the innermost one.
    :param default: value returned if the item does not exist.
    :param converter: optional function to convert the returned value.
    :returns: the value of the item.
    :raises KeyError: if the item does not exist and no default value is provided.
    """
    return core.get(_APP_CONFIG, *keys, default=default, converter=converter)


def has(*keys: ConfigKey) -> bool:
    """Checks whether the configuration of the current application has an item.

    :param keys: path of the item, from the outermost key to the innermost one.
    """
    return core.has(_APP_CONFIG, *keys)


def put(*keys: ConfigKey, value: ConfigValue, overwrite: bool = False) -> None:
    """Sets the value of an item in the configuration of the current application.

    :param keys: path of the item, from the outermost key to the innermost one.
    :param value: value of the item.
    :param overwrite: whether an existing value may be overwritten. Disabled by default.
    :raises KeyError: if the item, or one of its parents, already has a value and `overwrite` is
        disabled.
    """
    core.put(_APP_CONFIG, *keys, value=value, overwrite=overwrite)


def replace(*keys: ConfigKey, value: ConfigValue) -> None:
    """Sets the value of an item in the configuration of the current application, overwriting the
    existing one if any.

    :param keys: path of the item, from the outermost key to the innermost one.
    :param value: new value of the item.
    """
    core.replace(_APP_CONFIG, *keys, value=value)


def update(source: Mapping[ConfigKey, ConfigValue]) -> None:
    """Deeply updates the configuration of the current application.

    :param source: items to merge into the configuration.
    """
    core.update(_APP_CONFIG, source)


__all__ = ["configure", "get", "has", "put", "replace", "update"]
