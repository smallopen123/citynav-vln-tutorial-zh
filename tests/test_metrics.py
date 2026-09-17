import unittest

from citynav_tutorial.metrics import EpisodeResult, navigation_error, oracle_success, spl, success


class MetricTests(unittest.TestCase):
    def test_success_and_spl(self) -> None:
        result = EpisodeResult(
            final_xy=(19.0, 0.0),
            goal_xy=(0.0, 0.0),
            visited_xy=[(50.0, 0.0), (19.0, 0.0)],
            path_length=40.0,
            reference_path_length=30.0,
        )
        self.assertEqual(navigation_error(result), 19.0)
        self.assertTrue(success(result))
        self.assertTrue(oracle_success(result))
        self.assertAlmostEqual(spl(result), 0.75)

    def test_oracle_success_can_differ_from_final_success(self) -> None:
        result = EpisodeResult(
            final_xy=(100.0, 0.0),
            goal_xy=(0.0, 0.0),
            visited_xy=[(10.0, 0.0), (100.0, 0.0)],
            path_length=100.0,
            reference_path_length=50.0,
        )
        self.assertFalse(success(result))
        self.assertTrue(oracle_success(result))
        self.assertEqual(spl(result), 0.0)


if __name__ == "__main__":
    unittest.main()

