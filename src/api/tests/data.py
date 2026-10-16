from pathlib import Path
from typing import Any

TESTS_FOLDER = Path(__file__).parent
DATA_FOLDER = TESTS_FOLDER / "data"
CONFIG_FOLDER = DATA_FOLDER / "config"

STATE: dict[str, Any] = {
    "collisions": [
        {
            "ray": {
                "origin": {"x": 0.0, "y": 1.0, "z": 0.0},
                "direction": {"x": 1.0, "y": 0.0, "z": 0.0},
            },
            "point": {"x": 5.0, "y": 1.0, "z": 0.0},
        },
        {
            "ray": {
                "origin": {"x": 0.0, "y": 1.0, "z": 0.0},
                "direction": {"x": 0.0, "y": 0.0, "z": 1.0},
            },
            "point": {"x": 0.0, "y": 1.0, "z": 2.5},
        },
    ],
    "speed": {"x": 1.5, "y": 0.0, "z": -0.5},
}
"""A valid walker state, as sent by a client"""

__all__ = ["TESTS_FOLDER", "DATA_FOLDER", "CONFIG_FOLDER", "STATE"]
