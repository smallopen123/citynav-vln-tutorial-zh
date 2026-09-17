from __future__ import annotations

from math import atan2, degrees
import re

from .toy_env import Observation
from .types import Action


class GSMGreedyPolicy:
    """用“地标 + 方位关系”解析指令，再逐步朝地图目标飞行。

    支持“图书馆南侧 20 米”一类教学指令。真实论文会用神经网络和视觉
    grounding，本策略仅把核心的数据流显式化。
    """

    OFFSETS = {
        "东": (1.0, 0.0),
        "西": (-1.0, 0.0),
        "北": (0.0, 1.0),
        "南": (0.0, -1.0),
    }

    def __init__(self, instruction: str, gsm_landmarks: tuple[tuple[str, float, float], ...], stop_radius: float = 10.0):
        self.instruction = instruction
        self.stop_radius = stop_radius
        self.goal_xy = self._ground_instruction(gsm_landmarks)

    def _ground_instruction(self, gsm_landmarks: tuple[tuple[str, float, float], ...]) -> tuple[float, float]:
        match = re.search(r"([东西南北])侧\s*(\d+(?:\.\d+)?)\s*米", self.instruction)
        mentioned = [item for item in gsm_landmarks if item[0] in self.instruction]
        if not mentioned:
            raise ValueError("指令没有提到 GSM 中的任何已知地标。")

        # 有多个地标时，选择离“南侧/北侧……”关系词最近的前置地标。
        # 例如“从市政厅出发，到图书馆南侧 20 米”应以图书馆为参照。
        if match:
            relation_start = match.start()
            preceding = [item for item in mentioned if self.instruction.rfind(item[0], 0, relation_start) >= 0]
            selected = max(
                preceding or mentioned,
                key=lambda item: self.instruction.rfind(item[0], 0, relation_start),
            )
        else:
            selected = mentioned[-1]
        _, x, y = selected
        if not match:
            return x, y
        direction, distance_text = match.groups()
        dx, dy = self.OFFSETS[direction]
        distance = float(distance_text)
        return x + dx * distance, y + dy * distance

    @staticmethod
    def _angle_delta(target: float, current: float) -> float:
        return (target - current + 180.0) % 360.0 - 180.0

    def act(self, observation: Observation) -> Action:
        x, y = self.goal_xy
        dx, dy = x - observation.pose.x, y - observation.pose.y
        distance = (dx * dx + dy * dy) ** 0.5
        if distance <= self.stop_radius:
            return Action.STOP
        desired = degrees(atan2(dy, dx)) % 360.0
        delta = self._angle_delta(desired, observation.pose.heading_deg)
        if abs(delta) <= 22.5:
            return Action.FORWARD
        return Action.TURN_LEFT if delta > 0 else Action.TURN_RIGHT
