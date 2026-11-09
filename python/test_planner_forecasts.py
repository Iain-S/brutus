"""Bounded forecast tests without game assets or a model service."""

import unittest
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
from julius_gym.planner import Candidate


def observation(population, treasury):
    return {"population_total": np.array(population), "finance_treasury": np.array(treasury),
            "resources_food_stocks": np.array(0)}


class ForecastTests(unittest.TestCase):
    def test_runner_rejects_unbounded_forecast_horizons(self):
        runner = Path(__file__).parent / "examples" / "run_planner.py"
        for ticks in (-1, 8001):
            result = subprocess.run([sys.executable, str(runner), "--data-dir", "unused",
                                     "--lib-path", "unused", "--forecast-ticks", str(ticks)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("--forecast-ticks must be from 0 to 8000", result.stderr)

    def test_local_adapter_exposes_optional_forecast_columns(self):
        spec = importlib.util.spec_from_file_location("forecast_adapter", Path(__file__).parent / "examples" / "ollama_planner.py")
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        forecast = {"ticks": 800, "status": "completed", "population": 12, "food_stocks": 0,
                    "residents_with_food": 0, "health": 50, "farm_workers": 0, "treasury": 90}
        context = {"decision_id": 0, "forecast_policy": {"minimum_ticks": 800},
                   "candidates": [{"id": "housing", "forecast": forecast}]}
        compact = json.loads(adapter.request_body(context, "test-model", 96)["prompt"])
        self.assertEqual(compact["candidate_columns"][-1], "forecast")
        self.assertEqual(dict(zip(compact["forecast_columns"], compact["candidates"][0][-1])), forecast)
        self.assertEqual(compact["forecast_policy"], context["forecast_policy"])
        del context["forecast_policy"]
        context["candidates"] = [{"id": "wait"}]
        compact = json.loads(adapter.request_body(context, "test-model", 96)["prompt"])
        self.assertNotIn("forecast_columns", compact)
        self.assertEqual(len(compact["candidates"][0]), 4)

    def setUp(self):
        self.env = MagicMock()
        self.snapshot = self.env.snapshot.return_value.__enter__.return_value
        self.env.get_buildings.return_value = []
        self.env.get_population_info.return_value = {"health": 50}
        self.candidate = Candidate("housing", [(5, 1, 1)], "current", {})
        self.before = observation(0, 100)
        self.built = observation(0, 90)
        self.after = observation(12, 85)
        self.built_result = {"status": "completed", "steps": [{"action": (5, 1, 1)}]}

    def preview(self, execute, *, ticks=10, budget=20):
        from julius_gym.planner import preview_candidate
        with patch("julius_gym.planner.execute", execute), \
                patch("julius_gym.planner.fingerprint", return_value="current"):
            return preview_candidate(self.env, self.candidate, self.before, budget, ticks)

    def test_disabled_preserves_construction_only(self):
        execute = Mock(return_value=(self.built, self.built_result, False, False))
        result, outlay, forecast = self.preview(execute, ticks=0)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(outlay, 10)
        self.assertIsNone(forecast)
        self.assertEqual(execute.call_count, 1)
        self.snapshot.restore.assert_called_once()

    def test_continuation_is_bounded_and_cost_is_separate(self):
        execute = Mock(side_effect=[(self.built, self.built_result, False, False),
                                   (self.after, {"status": "completed", "steps": [{}] * 4}, False, False)])
        _, outlay, forecast = self.preview(execute, budget=5)
        self.assertEqual(outlay, 10)
        self.assertEqual(forecast["ticks"], 5)
        self.assertEqual(forecast["population"], 12)
        self.assertEqual(forecast["treasury"], 85)
        self.assertEqual(len(execute.call_args.args[1].actions), 4)
        self.assertEqual(execute.call_args.args[3], 4)
        self.snapshot.restore.assert_called_once()

    def test_terminal_continuation_is_reported_not_rejected(self):
        execute = Mock(side_effect=[(self.built, self.built_result, False, False),
                                   (self.after, {"status": "lost", "steps": [{}]}, True, False)])
        result, _, forecast = self.preview(execute)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(forecast["status"], "lost")
        self.assertEqual(forecast["ticks"], 2)

    def test_construction_victory_does_not_continue(self):
        execute = Mock(return_value=(self.built, {"status": "won", "steps": [{}]}, True, False))
        _, _, forecast = self.preview(execute)
        self.assertEqual(forecast["status"], "won")
        self.assertEqual(execute.call_count, 1)

    def test_failed_construction_is_not_forecast(self):
        execute = Mock(return_value=(self.built, {"status": "failed", "steps": [{}]}, False, False))
        _, _, forecast = self.preview(execute)
        self.assertIsNone(forecast)
        self.assertEqual(execute.call_count, 1)

    def test_wait_loss_is_forecast_without_continuation(self):
        self.candidate.id = "wait"
        execute = Mock(return_value=(self.after, {"status": "lost", "steps": [{}]}, True, False))
        _, _, forecast = self.preview(execute)
        self.assertEqual(forecast["status"], "lost")
        self.assertEqual(execute.call_count, 1)

    def test_construction_can_consume_entire_budget(self):
        execute = Mock(return_value=(self.built, self.built_result, False, False))
        _, _, forecast = self.preview(execute, budget=1)
        self.assertEqual(forecast["ticks"], 1)
        self.assertEqual(execute.call_count, 1)

    def test_exception_still_restores(self):
        execute = Mock(side_effect=RuntimeError("simulation failure"))
        with self.assertRaisesRegex(RuntimeError, "simulation failure"):
            self.preview(execute)
        self.snapshot.restore.assert_called_once()


if __name__ == "__main__":
    unittest.main()
