import importlib.metadata

from walker.trainer import get_package_version


def test_application_version() -> None:
    assert importlib.metadata.version("walker.trainer") == get_package_version()
