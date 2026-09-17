from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

from .types import Action, Episode, Pose


@dataclass(frozen=True)
class Observation:
    """教学版观测：数值字段模拟真实系统中的多模态输入。"""

    pose: Pose
    visible_landmarks: tuple[tuple[str, float], ...]
    gsm_landmarks: tuple[tuple[str, float, float], ...]
    rgb_hint: str
    depth_hint: str
    step_index: int


class ToyCityNavEnv:
    """纯标准库的简化 CityNav 环境。

    它不是官方 CityNav 模拟器。它保留了 episode、逐步观测、动作、STOP、
    成功半径和轨迹记录，用于在下载大型数据之前理解导航闭环。
    """

    def __init__(
        self,
        episode: Episode,
        step_size: float = 10.0,
        turn_angle_deg: float = 45.0,
        sensor_range: float = 55.0,
        success_radius: float = 12.0,
    ) -> None:
        self.episode = episode
        self.step_size = step_size
        self.turn_angle_deg = turn_angle_deg
        self.sensor_range = sensor_range
        self.success_radius = success_radius
        self.pose = episode.start
        self.path: list[Pose] = [self.pose]
        self.actions: list[Action] = []
        self.done = False

    def reset(self) -> Observation:
        self.pose = self.episode.start
        self.path = [self.pose]
        self.actions = []
        self.done = False
        return self.observe()

    def observe(self) -> Observation:
        visible: list[tuple[str, float]] = []
        for landmark in self.episode.landmarks:
            distance = ((self.pose.x - landmark.x) ** 2 + (self.pose.y - landmark.y) ** 2) ** 0.5
            if distance <= self.sensor_range:
                visible.append((landmark.name, round(distance, 1)))
        visible.sort(key=lambda item: item[1])

        rgb_hint = "可见：" + ("、".join(name for name, _ in visible) or "暂无显著地标")
        nearest = visible[0][1] if visible else self.sensor_range
        depth_hint = f"最近显著物约 {nearest:.1f} m"
        gsm = tuple((item.name, item.x, item.y) for item in self.episode.landmarks)
        return Observation(self.pose, tuple(visible), gsm, rgb_hint, depth_hint, len(self.actions))

    def step(self, action: Action) -> tuple[Observation, float, bool, dict[str, float | bool]]:
        if self.done:
            raise RuntimeError("episode 已结束，请先调用 reset()。")

        heading = self.pose.heading_deg
        x, y, z = self.pose.x, self.pose.y, self.pose.z
        if action == Action.TURN_LEFT:
            heading = (heading + self.turn_angle_deg) % 360
        elif action == Action.TURN_RIGHT:
            heading = (heading - self.turn_angle_deg) % 360
        elif action == Action.FORWARD:
            x += self.step_size * cos(radians(heading))
            y += self.step_size * sin(radians(heading))
        elif action == Action.ASCEND:
            z += self.step_size
        elif action == Action.DESCEND:
            z = max(0.0, z - self.step_size)
        elif action == Action.STOP:
            self.done = True

        self.pose = Pose(x, y, z, heading)
        self.actions.append(action)
        self.path.append(self.pose)
        if len(self.actions) >= self.episode.max_steps:
            self.done = True

        distance = self.pose.planar_distance_to(self.episode.goal)
        reward = -distance / 100.0
        if action == Action.STOP and distance <= self.success_radius:
            reward += 1.0
        info = {
            "distance_to_goal": distance,
            "success": self.done and distance <= self.success_radius,
        }
        return self.observe(), reward, self.done, info

