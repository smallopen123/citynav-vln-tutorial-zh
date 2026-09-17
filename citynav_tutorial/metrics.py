from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Sequence


@dataclass(frozen=True)
class EpisodeResult:
    final_xy: tuple[float, float]
    goal_xy: tuple[float, float]
    visited_xy: Sequence[tuple[float, float]]
    path_length: float
    reference_path_length: float


def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def navigation_error(result: EpisodeResult) -> float:
    """NE：结束位置到目标的欧氏距离，越小越好。"""
    return _distance(result.final_xy, result.goal_xy)


def success(result: EpisodeResult, radius: float = 20.0) -> bool:
    """SR 的单 episode 判定：最终停止位置是否进入成功半径。"""
    return navigation_error(result) <= radius


def oracle_success(result: EpisodeResult, radius: float = 20.0) -> bool:
    """OSR 的单 episode 判定：途中是否曾进入成功半径。"""
    return any(_distance(point, result.goal_xy) <= radius for point in result.visited_xy)


def spl(result: EpisodeResult, radius: float = 20.0) -> float:
    """SPL：成功率乘以路径效率。失败时为 0。"""
    if not success(result, radius):
        return 0.0
    shortest = result.reference_path_length
    return shortest / max(shortest, result.path_length, 1e-9)

