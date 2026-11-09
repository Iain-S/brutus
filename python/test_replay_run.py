"""Replay trace parsing and divergence checks independent of game data."""

import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("replay_run", Path(__file__).parent / "examples" / "replay_run.py")
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class ReplayTests(unittest.TestCase):
    def test_both_log_shapes_preserve_observation_steps(self):
        action = {"action": [5, 1, 1], "message": "Built housing", "reward": 0.1}
        observation = {"action": [0, 0, 0], "message": "No action taken", "reward": 0.01}
        self.assertEqual(list(replay.recorded_steps([{"mission": {}}, action, observation])), [action, observation])
        self.assertEqual(list(replay.recorded_steps([{"result": {"steps": [action, observation]}}])), [action, observation])

    def test_divergence_and_nonfinite_rewards_are_rejected(self):
        expected = {"message": "Built housing", "reward": 0.1}
        replay.assert_step_matches(expected, dict(expected), 1)
        for change in ({"message": "Construction failed"}, {"reward": 0.2}, {"reward": float("nan")}):
            with self.subTest(change=change), self.assertRaisesRegex(AssertionError, "tick 7"):
                replay.assert_step_matches(expected, {**expected, **change}, 7)


if __name__ == "__main__":
    unittest.main()
