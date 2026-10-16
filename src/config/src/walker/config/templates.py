"""Templates to validate configuration values."""

import pathlib
from typing import Any

import confuse


class Path(confuse.Template):
    """A template that validates strings as :py:class:`pathlib.Path` objects."""

    def __init__(
        self,
        default: pathlib.Path | str | None = confuse.REQUIRED,  # type: ignore[assignment]
    ) -> None:
        """Initializes a path template with a default value."""
        if isinstance(default, str):
            default = pathlib.Path(default)
        elif (
            not isinstance(default, pathlib.Path)
            and default is not None
            and default is not confuse.REQUIRED
        ):
            raise ValueError(
                f"If provided, 'default' must be a valid path or 'None', got '{default}'"
            )

        super().__init__(default)

    def convert(self, value: Any, view: confuse.ConfigView) -> pathlib.Path:
        """Converts `value` to a :py:class:`pathlib.Path` instance.

        An error is raised if the value cannot be converted.
        """
        if isinstance(value, pathlib.Path):
            return value
        if not isinstance(value, str):
            self.fail(f"must be a string, not '{type(value).__name__}'", view, type_error=True)

        return pathlib.Path(value)


__all__ = ["Path"]
