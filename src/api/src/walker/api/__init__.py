"""An API for autonomous movements of bots in unknown locations."""

import importlib.metadata

from . import patches

# Applies required patches BEFORE anything else
patches.patchify()


def get_package_name() -> str:
    """Gets package name."""
    return __name__


def get_package_version(package_name: str | None = None) -> str:
    """Gets package version."""
    if package_name is None:
        package_name = get_package_name()

    return importlib.metadata.version(package_name)


__version__ = get_package_version()

APP_NAME = "WALKER_API"


__all__ = [
    "APP_NAME",
    "__version__",
    "get_package_name",
    "get_package_version",
]
