from typing import Any

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

RECORD: dict[str, Any] = {
    "session": "1b4e28ba-2fa1-41d2-883f-0016d3cca427",
    "walker": "Walker",
    "scene": "scene",
    "frame": 42,
    "time": 4.2,
    "observation": OBSERVATION,
}
"""A valid record with only the fields shared by all the behaviours of a walker"""

TRAINING_RECORD: dict[str, Any] = RECORD | {
    "desired_velocity": {"x": 3.5, "y": 0.0, "z": 0.0},
    "target": {"x": 10.0, "y": 0.0, "z": 0.0},
}
"""A valid record of a training walker, as sent by a client"""

PATROLLING_RECORD: dict[str, Any] = RECORD | {
    "contacts": 2,
    "walk": {"x": 0.0, "y": 0.0, "z": 3.5},
}
"""A valid record of a patrolling walker, as sent by a client"""

__all__ = ["OBSERVATION", "RECORD", "TRAINING_RECORD", "PATROLLING_RECORD"]
