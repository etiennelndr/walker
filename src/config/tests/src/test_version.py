import importlib.metadata

from walker.config import get_package_version


def test_application_version() -> None:
    assert importlib.metadata.version("walker.config") == get_package_version()
