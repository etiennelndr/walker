import importlib.metadata

from walker.core import get_package_version


def test_application_version() -> None:
    assert importlib.metadata.version("walker.core") == get_package_version()
