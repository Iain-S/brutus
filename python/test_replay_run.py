"""Replay trace parsing and divergence checks independent of game data."""

import importlib.util
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

spec = importlib.util.spec_from_file_location("replay_run", Path(__file__).parent / "examples" / "replay_run.py")
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class ReplayTests(unittest.TestCase):
    def test_optional_imperial_state_is_compared_strictly(self):
        env = SimpleNamespace(get_imperial_state=Mock(return_value={"personal_savings": 100, "favor": 53}))
        missing = SimpleNamespace(exists=lambda: False)
        self.assertFalse(replay.verify_imperial_state(env, missing))
        env.get_imperial_state.assert_not_called()
        path = SimpleNamespace(exists=lambda: True, read_text=lambda **kwargs: '{"personal_savings":100,"favor":53}')
        self.assertTrue(replay.verify_imperial_state(env, path))
        env.get_imperial_state.return_value["personal_savings"] = 99
        with self.assertRaisesRegex(AssertionError, "imperial"):
            replay.verify_imperial_state(env, path)

    def test_optional_food_diagnostics_are_compared_strictly(self):
        env = SimpleNamespace(get_food_supply=Mock(return_value={"schema_version": 1, "buildings": []}))
        path = SimpleNamespace(exists=lambda: False)
        self.assertFalse(replay.verify_food_supply(env, path))
        env.get_food_supply.assert_not_called()
        path = SimpleNamespace(exists=lambda: True,
                               read_text=lambda **kwargs: '{"schema_version":1,"buildings":[]}')
        self.assertTrue(replay.verify_food_supply(env, path))
        env.get_food_supply.return_value = {"schema_version": 1, "buildings": [{"id": 1}]}
        with self.assertRaisesRegex(AssertionError, "food supply"):
            replay.verify_food_supply(env, path)

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
