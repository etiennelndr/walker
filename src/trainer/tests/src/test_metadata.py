import pytest

from walker.trainer import get_package_name, get_package_version


def test_get_package_name() -> None:
    assert get_package_name() == "walker.trainer"


@pytest.mark.parametrize(
    ("package_name", "package_version"),
    [
        pytest.param(None, get_package_version()),
        pytest.param("walker.trainer", get_package_version()),
        pytest.param("pytest", "9.1.1", id="test-dependency"),
        pytest.param("unknown", None, id="unknown-dependency"),
    ],
)
def test_get_package_version(package_name: str | None, package_version: str | None) -> None:
    assert get_package_version(package_name) == package_version
