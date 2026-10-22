"""Common building blocks for Walker's Python projects."""

import importlib.metadata


def get_package_name() -> str:
    """Gets package name."""
    return __name__


def get_package_version(package_name: str | None = None) -> str | None:
    """Gets package version."""
    if package_name is None:
        package_name = get_package_name()

    try:
        return importlib.metadata.version(package_name)
    except ValueError, importlib.metadata.PackageNotFoundError:
        return None


__version__ = get_package_version()


__all__ = ["__version__", "get_package_name", "get_package_version"]
