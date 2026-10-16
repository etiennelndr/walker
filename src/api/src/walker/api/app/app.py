"""Application factory and configuration for the Walker API.

This module provides the main application factory, configuration templates, and lifecycle
management for the ASGI application. It handles error handling and blueprint registration.
"""

from collections.abc import Callable, Iterable

from quart import Blueprint, Quart
from quart_schema import Info, QuartSchema, tag_blueprint
from quart_schema import OpenAPIProvider as _OpenAPIProvider
from quart_schema.openapi import QUART_SCHEMA_OPERATION_ID_ATTRIBUTE

import walker.api.attrs.config as wac
import walker.config as wc
from walker.api import APP_NAME, get_package_version
from walker.api.logging import configure_logger

from .config import APP_CONFIG_TEMPLATE
from .errors import handle_app_error


class OpenAPIProvider(_OpenAPIProvider):
    """A custom OpenAPI provider."""

    def operation_id(self, method: str, path: str, func: Callable) -> str | None:
        """Returns a unique operation ID.

        Only the function name is used to generate an operation ID.
        """
        return getattr(func, QUART_SCHEMA_OPERATION_ID_ATTRIBUTE, func.__name__)


def create_app(blueprints: Iterable[Blueprint]) -> Quart:
    """Creates and configures an application instance.

    The main ASGI application is initialized with all necessary configuration, middlewares and
    blueprints.

    :param blueprints: blueprints served by the application.
    :returns: a fully configured application instance.
    """
    app = Quart(__name__, static_folder=None, template_folder=None)
    app.url_map.strict_slashes = False
    # Do not wait for the background tasks to end
    app.config["BACKGROUND_TASK_SHUTDOWN_TIMEOUT"] = 0

    # Load and apply application configuration
    wc.app.configure(app.config, APP_NAME, app_template=APP_CONFIG_TEMPLATE)

    # Configure application logger before any other operations
    configure_logger(app.logger, logger_config=wc.get(app.config, wac.App.LOGGING))

    # Register global error handler
    app.register_error_handler(Exception, handle_app_error)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
        # Tag each blueprint with its name to group endpoints by their blueprint membership in the
        # OpenAPI documentation
        tag_blueprint(blueprint, [blueprint.name.capitalize()])

    # Configure QuartSchema for validation of HTTP requests and responses
    app_schema = QuartSchema(
        conversion_preference="msgspec",
        openapi_path=wc.get(
            app.config,
            wac.App.OPENAPI,
            wac.OpenAPI.ENDPOINT,
            default=None,
        ),
        info=Info(
            title="Walker API",
            version=get_package_version(),
        ),
        openapi_provider_class=OpenAPIProvider,
    )
    app_schema.init_app(app)

    return app


__all__ = ["create_app"]
