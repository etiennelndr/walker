from pathlib import Path
from typing import Any

TESTS_FOLDER = Path(__file__).parent
DATA_FOLDER = TESTS_FOLDER / "data"
CONFIG_FOLDER = DATA_FOLDER / "config"

OBSERVATION: dict[str, Any] = {
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
    "velocity": {"x": 1.5, "y": 0.0, "z": -0.5},
}
"""A valid walker observation, as sent by a client"""

TRAINING_RECORD: dict[str, Any] = {
    "session": "1b4e28ba-2fa1-41d2-883f-0016d3cca427",
    "walker": "Walker",
    "scene": "scene",
    "frame": 42,
    "time": 4.2,
    "observation": OBSERVATION,
    "desired_velocity": {"x": 3.5, "y": 0.0, "z": 0.0},
    "target": {"x": 10.0, "y": 0.0, "z": 0.0},
}
"""A valid record of a training walker, as sent by a client"""

__all__ = ["TESTS_FOLDER", "DATA_FOLDER", "CONFIG_FOLDER", "OBSERVATION", "TRAINING_RECORD"]
