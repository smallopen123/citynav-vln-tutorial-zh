import unittest

from citynav_tutorial.policies import GSMGreedyPolicy
from citynav_tutorial.toy_env import ToyCityNavEnv
from citynav_tutorial.types import Episode, Landmark, Pose


class ToyNavigationTests(unittest.TestCase):
    def test_policy_completes_episode(self) -> None:
        episode = Episode(
            episode_id="test",
            instruction="飞到图书馆南侧 20 米并停止。",
            start=Pose(0.0, 0.0, heading_deg=0.0),
            goal=Pose(80.0, 20.0),
            landmarks=(Landmark("图书馆", 80.0, 40.0),),
            max_steps=30,
        )
        env = ToyCityNavEnv(episode)
        observation = env.reset()
        policy = GSMGreedyPolicy(episode.instruction, observation.gsm_landmarks)
        while not env.done:
            observation, _, _, info = env.step(policy.act(observation))
        self.assertTrue(info["success"])
        self.assertLessEqual(info["distance_to_goal"], env.success_radius)

    def test_relation_uses_nearest_preceding_landmark(self) -> None:
        policy = GSMGreedyPolicy(
            "从市政厅出发，到图书馆南侧 20 米。",
            (("市政厅", 0.0, 0.0), ("图书馆", 80.0, 40.0)),
        )
        self.assertEqual(policy.goal_xy, (80.0, 20.0))


if __name__ == "__main__":
    unittest.main()
