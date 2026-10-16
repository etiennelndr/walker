"""Module for defining, encoding, and decoding strongly typed API resources."""

from __future__ import annotations

from abc import ABCMeta
from typing import Any, ClassVar, Self, cast

import msgspec.json
from msgspec import UNSET, DecodeError, EncodeError, Struct, StructMeta, UnsetType, to_builtins
from msgspec.structs import replace
from quart import Response
from werkzeug.datastructures import Headers

type APIResourceEncoder = msgspec.json.Encoder
type APIResourceDecoder[T] = msgspec.json.Decoder[T]


class LazyAPIResourceDecoder:
    """Descriptor that lazily instantiates an :py:class:`APIResourceDecoder`.

    This descriptor is attached to :py:class:`APIResource.decoder` during subclass initialization.
    When the ``decoder`` attribute is first accessed on a subclass, the descriptor creates a new
    :py:class:`APIResourceDecoder` instance bound to that subclass, assigns it to the subclass
    attribute, and returns it. Subsequent accesses use the same instance.

    This ensures that every :py:class:`APIResource` subclass receives its own dedicated decoder
    object without requiring explicit assignment in each subclass.
    """

    def __get__[T: APIResource](self, _, cls: type[T]) -> APIResourceDecoder[T]:
        cls_decoder = APIResourceDecoder.__value__(cls)
        # Replace this instance with the newly created decoder to avoid calling this descriptor on
        # each call to 'APIResource.decoder'
        cls.decoder = cls_decoder
        return cls_decoder


class APIResourceMeta(StructMeta, ABCMeta):
    """Metaclass for API resources.

    Extends :py:class:`msgspec.StructMeta` to automatically configure all API resource classes with
    keyword-only arguments. It also extends :py:class:`abc.ABCMeta`, so that API resources may
    declare abstract methods.
    """

    def __new__(
        cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **struct_config: Any
    ) -> APIResourceMeta:
        """Creates a new API resource class with keyword-only fields.

        :param name: name of the class being created.
        :param bases: base classes of the new class.
        :param namespace: class namespace dictionary.
        :param struct_config: additional configuration options.
        :returns: the newly created class.
        """
        # `msgspec.defstruct` explicitly includes `__slots__` in the namespace of the generated
        # class. When `StructMeta` receives a namespace with `__slots__` already set, it conflicts
        # with its own internal slot management, causing a crash. We remove it here to let
        # `StructMeta` handle slots itself as it normally would.
        # See https://github.com/jcrist/msgspec/issues/974.
        namespace.pop("__slots__", None)
        struct_config["kw_only"] = True
        return super().__new__(cls, name, bases, namespace, **struct_config)


class APIResource(Struct, metaclass=APIResourceMeta, kw_only=True):
    """Base class for all API resources."""

    encoder: ClassVar[APIResourceEncoder] = msgspec.json.Encoder(
        # Deterministic order is activated to ensure buffers consistency
        order="deterministic"
    )
    """A shared encoder instance for serializing resource instances to JSON-compatible
    representations
    """
    decoder: ClassVar[APIResourceDecoder[Self]]
    """A lazily-initialized decoder instance specific to each subclass, responsible for parsing JSON
    data into resource objects
    """
    response_class: ClassVar[type[Response]] = Response
    """The class of the responses built from resource instances"""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        cls.decoder = cast(APIResourceDecoder[Self], LazyAPIResourceDecoder())

    def replace(self, **fields: Any) -> Self:
        """Return a new resource instance with the specified fields replaced.

        Fields are replaced with values from ``**fields``. Non-provided fields are kept as-is.

        This is a convenience wrapper around :py:func:`msgspec.structs.replace`.

        :param fields: field names and new values to apply to the returned instance.
        :returns: a new instance of the resource with updated fields.
        """
        return replace(self, **fields)

    def as_dict(self) -> dict[str, Any]:
        """Converts this resource instance to a :py:class:`dict`.

        It converts the resource instance into a :py:class:`dict` where keys are field names and
        values are the corresponding field values.

        This is a convenience wrapper around :py:func:`msgspec.to_builtins`.

        :returns: a :py:class:`dict` of field names to their values.
        """
        return to_builtins(
            self,
            # Deterministic order is activated to ensure consistent key ordering across calls
            order="deterministic",
        )

    def as_response(
        self,
        *,
        status: int | None = None,
        headers: dict | Headers | None = None,
    ) -> Response:
        """Converts this resource instance to a response.

        :param status: status code of the response.
        :param headers: headers to attach to the response.
        :returns: an instance of :py:attr:`response_class` whose body is this encoded resource.
        """
        return self.response_class(
            self.encode(),
            status=status,
            headers=headers,
            mimetype="application/json",
        )

    def encode(self) -> bytes:
        """Encodes this resource instance into a JSON-compatible representation.

        :returns: a JSON representation of this resource.
        """
        return self.encoder.encode(self)

    @classmethod
    def decode(cls, value: bytes | str | Any) -> Self:
        """Decodes a JSON-compatible representation into a resource instance.

        If ``value`` is JSON data (:py:class:`bytes` or :py:class:`str`), the decoder associated
        with this subclass is used. If ``value`` is a Python structure (e.g. :py:class:`dict`), it
        will be coerced into the correct type using :py:func:`msgspec.convert`.

        :param value: input to decode. JSON bytes, JSON string, or already-parsed Python structure.
        :returns: a fully decoded and validated resource instance.
        """
        if isinstance(value, bytes | str):
            return cls.decoder.decode(value)
        return msgspec.convert(value, cls)

    @classmethod
    def partial[T: type[APIResource]](
        cls: T,
        *,
        exclude: set[str] | None = None,
        suffix: str = "Partial",
    ) -> T:
        """Dynamically creates a partial version of this resource with all fields made optional.

        This is useful for defining PATCH payloads without having to manually declare a separate
        struct where every field is ``UNSET``-defaulted. The generated struct is a subclass of
        :py:class:`APIResource` and inherits all its methods.

        :Example:

        >>> StatePartial = State.partial(exclude={"speed"})
        >>> StatePatch = State.partial(exclude={"speed"}, suffix="Patch")

        :param exclude: field names to omit entirely from the generated struct.
        :param suffix: suffix of the newly created resource name. Defaults to `Partial`.
        :returns: a new :py:class:`APIResource` subclass named ``{ClassName}{suffix}`` where every
            included field has been widened to ``X | None | UnsetType`` with a default of
            :py:data:`msgspec.UNSET`.
        """
        exclude = exclude or set()

        return cast(
            T,
            msgspec.defstruct(
                f"{cls.__name__}{suffix}",
                [
                    (field.name, field.type | None | UnsetType, UNSET)
                    for field in msgspec.structs.fields(cls)
                    if field.name not in exclude
                ],
                bases=cls.__bases__,
            ),
        )


APIResourceEncodingError = EncodeError
"""An error occurred while encoding an API resource"""
APIResourceDecodingError = DecodeError
"""An error occurred while decoding an API resource"""


__all__ = [
    "APIResource",
    "APIResourceEncodingError",
    "APIResourceDecodingError",
]
