from __future__ import annotations

import json
from math import hypot
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from citynav_tutorial.metrics import EpisodeResult, navigation_error, oracle_success, spl, success
from citynav_tutorial.policies import GSMGreedyPolicy
from citynav_tutorial.toy_env import ToyCityNavEnv
from citynav_tutorial.types import Episode, Landmark, Pose


def load_episode(path: Path) -> Episode:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Episode(
        episode_id=raw["episode_id"],
        instruction=raw["instruction"],
        start=Pose(**raw["start"]),
        goal=Pose(**raw["goal"]),
        landmarks=tuple(Landmark(**item) for item in raw["landmarks"]),
        reference_path_length=raw["reference_path_length"],
        max_steps=raw["max_steps"],
    )


def path_length(path: list[Pose]) -> float:
    return sum(hypot(b.x - a.x, b.y - a.y) for a, b in zip(path, path[1:]))


def main() -> None:
    episode = load_episode(ROOT / "examples" / "toy_citynav.json")
    env = ToyCityNavEnv(episode)
    observation = env.reset()
    policy = GSMGreedyPolicy(episode.instruction, observation.gsm_landmarks)

    print(f"Episode: {episode.episode_id}")
    print(f"指令: {episode.instruction}")
    print(f"语言落地后的地图目标: ({policy.goal_xy[0]:.1f}, {policy.goal_xy[1]:.1f})")
    print("\nstep | pose(x,y,h)       | observation             | action      | distance")
    print("-" * 83)
    while not env.done:
        action = policy.act(observation)
        observation, _, done, info = env.step(action)
        visible = "、".join(name for name, _ in observation.visible_landmarks) or "无"
        pose = observation.pose
        print(
            f"{observation.step_index:>4} | ({pose.x:>4.0f},{pose.y:>4.0f},{pose.heading_deg:>3.0f}°) "
            f"| 可见:{visible:<18.18} | {action.value:<11} | {info['distance_to_goal']:>6.1f} m"
        )
        if done:
            break

    result = EpisodeResult(
        final_xy=(env.pose.x, env.pose.y),
        goal_xy=(episode.goal.x, episode.goal.y),
        visited_xy=[(item.x, item.y) for item in env.path],
        path_length=path_length(env.path),
        reference_path_length=episode.reference_path_length,
    )
    print("\n评测")
    print(f"NE  = {navigation_error(result):.2f} m")
    print(f"SR  = {int(success(result))}")
    print(f"OSR = {int(oracle_success(result))}")
    print(f"SPL = {spl(result):.3f}")


if __name__ == "__main__":
    main()

