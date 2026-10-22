"""QuartSchema patches."""

from functools import wraps
from http import HTTPStatus
from typing import Any, cast

import msgspec.json
import quart_schema.conversion
import quart_schema.mixins
import quart_schema.validation
from loguru import logger
from quart import Response, current_app
from quart_schema import (
    PydanticDumpOptions,
    ResponseSchemaValidationError,
    SchemaValidationError,
)
from quart_schema.typing import Model
from quart_schema.validation import QUART_SCHEMA_RESPONSE_ATTRIBUTE, ResponseHeadersValidationError
from werkzeug.wrappers import Response as WerkzeugResponse

from walker.api.http.error import HTTPError
from walker.api.http.response import make_resource_response
from walker.api.middlewares import Middleware
from walker.api.route import pack_route_response, unpack_route_response
from walker.api.typing import Route, RouteResponse, RouteResponseValue, Websocket
from walker.core.resources import Resource, ResourceDecodingError

from ._utils import copy_function

model_load_unpatched = copy_function(quart_schema.conversion.model_load)
model_dump_unpatched = copy_function(quart_schema.conversion.model_dump)
model_schema_unpatched = copy_function(quart_schema.conversion.model_schema)
validate_response_unpatched = copy_function(quart_schema.validation.validate_response)
send_as_unpatched = copy_function(quart_schema.mixins.WebsocketMixin.send_as)


def patchify() -> None:  # noqa: PLR0915
    """Patches QuartSchema functions for improved integration.

    Replaces QuartSchema's `model_load` implementation to use Resource's native decoder
    when handling Resource subclasses, significantly improving performance. Falls back
    to the original QuartSchema implementation for all other model types.
    """

    def model_load_patched[T](  # type: ignore[return]
        data: T | dict | list,
        model_class: type[T],
        exception_class: type[Exception],
        *,
        decamelize: bool = False,
        preference: str | None = None,
    ) -> T:
        """Loads and validates data into a model instance with optimized decoding.

        :param data: dictionary or list of data to validate and load.
        :param model_class: target model class for validation.
        :param exception_class: exception type to raise on validation errors.
        :param decamelize: whether to convert keys from camelCase to snake_case.
        :param preference: preferred library for model loading.
        :returns: validated and loaded model instance.
        :raises exception_class: when validation fails for non-Resource models.
        :raises HTTPError: when validation fails for Resource models or when a Resource of the
            wrong type is provided.
        """
        if issubclass(model_class, Resource):
            if isinstance(data, model_class):
                return data
            if isinstance(data, Resource):
                logger.error(
                    f"A resource of the wrong type has been provided to 'model_load'"
                    f" (got '{type(data).__name__}' instead of '{model_class.__name__}')"
                )
                HTTPError.INTERNAL_ERROR.abort()

            try:
                return model_class.decode(data)
            except ResourceDecodingError as err:
                raise exception_class(err)

        if issubclass(model_class, str | bytes) and not isinstance(data, model_class):
            logger.error(
                f"A data of the wrong type has been provided to 'model_load'"
                f" (got '{type(data).__name__}' instead of '{model_class.__name__}')"
            )
            HTTPError.INTERNAL_ERROR.abort()

        return model_load_unpatched(
            cast(dict | list, data),
            model_class,
            exception_class,
            decamelize=decamelize,
            preference=preference,
        )

    quart_schema.conversion.model_load.__code__ = model_load_patched.__code__
    # Injects this module's globals because this patched function introduces dependencies on
    # project-specific classes that don't exist in QuartSchema's original implementation
    quart_schema.conversion.model_load.__globals__.update(model_load_patched.__globals__)

    def model_dump_patched(
        raw: RouteResponseValue,
        *,
        camelize: bool = False,
        kebabize: bool = False,
        preference: str | None = None,
        pydantic_kwargs: PydanticDumpOptions | None = None,
    ) -> Response | dict | list:
        """Dumps data with optimized encoding for resources.

        :param raw: the response value to serialize.
        :param camelize: whether to convert keys to camelCase.
        :param kebabize: whether to convert keys to kebab-case.
        :param preference: preferred library for model dumping.
        :param pydantic_kwargs: additional options for Pydantic model dumping.
        :returns: a :py:class:`~quart.Response` instance or a JSON-compatible dictionary or list.
        """
        if isinstance(raw, Resource):
            return make_resource_response(raw)

        return model_dump_unpatched(
            raw,
            camelize=camelize,
            kebabize=kebabize,
            preference=preference,
            pydantic_kwargs=pydantic_kwargs,
        )

    quart_schema.conversion.model_dump.__code__ = model_dump_patched.__code__
    # Injects this module's globals because this patched function introduces dependencies on
    # project-specific classes that don't exist in QuartSchema's original implementation
    quart_schema.conversion.model_dump.__globals__.update(model_dump_patched.__globals__)

    def model_schema_patched(
        model_class: type,
        *,
        preference: str | None = None,
        schema_mode: quart_schema.conversion.JsonSchemaMode = "validation",
    ) -> dict:
        """Generates a JSON schema for a model class with proper MsgSpec component handling.

        Extends the base model schema generation to correctly include component definitions in the
        schema's `$defs` key when working with Resource models, making the OpenAPI
        `components.schemas` section properly populated.

        :param model_class: the model class for which to generate the JSON schema.
        :param preference: preferred library for model schema.
        :param schema_mode: the mode for schema generation, either "validation" or "serialization".
        :returns: a dictionary containing the JSON schema with embedded component definitions.
        """
        if issubclass(model_class, Resource | str | bytes):
            return msgspec.json.schema(
                model_class, ref_template=quart_schema.conversion.MSGSPEC_REF_TEMPLATE
            )

        return model_schema_unpatched(model_class, preference=preference, schema_mode=schema_mode)

    quart_schema.conversion.model_schema.__code__ = model_schema_patched.__code__
    # Injects this module's globals because this patched function introduces dependencies on
    # project-specific classes that don't exist in QuartSchema's original implementation
    quart_schema.conversion.model_schema.__globals__.update(model_schema_patched.__globals__)

    def validate_response_patched(
        model_class: type,
        status_code: int = HTTPStatus.OK,
        headers_model_class: type | None = None,
    ) -> Middleware:
        """Validates the response data and (optionally) headers against specified models."""

        def _decorator[**P, T: RouteResponseValue](route: Route[P, T]) -> Route[P, T]:
            schemas = getattr(route, QUART_SCHEMA_RESPONSE_ATTRIBUTE, {})
            schemas[status_code] = (model_class, headers_model_class)
            setattr(route, QUART_SCHEMA_RESPONSE_ATTRIBUTE, schemas)

            @wraps(route)
            async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse[T]:
                response = await route(*args, **kwargs)
                response_value, response_status, response_headers = unpack_route_response(response)

                if response_status is not None:
                    status = response_status
                elif isinstance(response_value, (Response, WerkzeugResponse)):
                    status = response_value.status_code
                else:
                    status = HTTPStatus.OK

                if isinstance(response_value, Response | WerkzeugResponse):
                    if status == status_code:
                        raise RuntimeError("Cannot validate Response instance")
                    else:
                        return response

                if status == status_code:
                    if type(response_value) is not model_class:
                        response_value = quart_schema.conversion.model_load(
                            response_value,  # type: ignore
                            model_class,
                            ResponseSchemaValidationError,
                        )

                    if headers_model_class is not None:
                        if type(response_headers) is not headers_model_class:
                            response_headers = quart_schema.conversion.convert_headers(
                                response_headers,  # type: ignore
                                headers_model_class,
                                ResponseHeadersValidationError,
                            )

                    return pack_route_response(
                        response_value,
                        response_status,
                        response_headers,
                    )

                return response

            return _wrapper

        return _decorator

    quart_schema.validation.validate_response.__code__ = validate_response_patched.__code__
    # Injects this module's globals because this patched function introduces dependencies on
    # project-specific classes that don't exist in QuartSchema's original implementation
    quart_schema.validation.validate_response.__globals__.update(
        validate_response_patched.__globals__
    )

    async def send_as_patched(self: Websocket, value: Any, model_class: type[Model]) -> None:
        """Validates a value against a model class and sends it through the websocket.

        The patched `model_dump` dumps resources into a response, which can't be sent as JSON:
        the body of this response, already encoded in JSON, is sent as is instead.

        :param value: the value to send.
        :param model_class: the model class to validate the value against.
        """
        if type(value) is not model_class:
            value = quart_schema.conversion.model_load(
                value,
                model_class,
                SchemaValidationError,
                preference=current_app.config["QUART_SCHEMA_CONVERSION_PREFERENCE"],
            )

        data = quart_schema.conversion.model_dump(
            value,
            camelize=current_app.config["QUART_SCHEMA_CONVERT_CASING"],
            preference=current_app.config["QUART_SCHEMA_CONVERSION_PREFERENCE"],
            pydantic_kwargs=current_app.config["QUART_SCHEMA_PYDANTIC_DUMP_OPTIONS"],
        )

        if isinstance(data, Response):
            body = await data.get_data(as_text=True)
            await self.send(body)
        else:
            await self.send_json(data)

    quart_schema.mixins.WebsocketMixin.send_as.__code__ = send_as_patched.__code__
    # Injects this module's globals because this patched function introduces dependencies on
    # project-specific classes that don't exist in QuartSchema's original implementation
    quart_schema.mixins.WebsocketMixin.send_as.__globals__.update(send_as_patched.__globals__)


__all__ = ["patchify"]
