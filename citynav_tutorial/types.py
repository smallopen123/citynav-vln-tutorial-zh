from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import hypot


class Action(str, Enum):
    """教学环境使用的离散无人机动作。"""

    FORWARD = "FORWARD"
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"
    ASCEND = "ASCEND"
    DESCEND = "DESCEND"
    STOP = "STOP"


@dataclass(frozen=True)
class Pose:
    x: float
    y: float
    z: float = 50.0
    heading_deg: float = 0.0

    def planar_distance_to(self, other: "Pose") -> float:
        return hypot(self.x - other.x, self.y - other.y)


@dataclass(frozen=True)
class Landmark:
    name: str
    x: float
    y: float
    category: str = "building"


@dataclass(frozen=True)
class Episode:
    episode_id: str
    instruction: str
    start: Pose
    goal: Pose
    landmarks: tuple[Landmark, ...] = field(default_factory=tuple)
    reference_path_length: float = 0.0
    max_steps: int = 60

