from pathlib import Path

TESTS_FOLDER = Path(__file__).parent
DATA_FOLDER = TESTS_FOLDER / "data"
CONFIG_FOLDER = DATA_FOLDER / "config"

__all__ = ["TESTS_FOLDER", "DATA_FOLDER", "CONFIG_FOLDER"]
