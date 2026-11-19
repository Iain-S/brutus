"""Food summaries and observed cycle history require no game assets or model."""

import importlib.util
import json
from pathlib import Path
import unittest
from types import SimpleNamespace


def supply(rows):
    return {"schema_version": 1, "units_per_load": 100, "buildings": rows}


def storage(identifier, kind, food):
    return {"id": identifier, "kind": kind, "x": identifier, "y": 3, "workers": 2,
            "workers_required": 5, "road_access": 1, "food_units": [food, 0, 0, 0],
            "free_space_units": 2400 - food}


class FeedbackTests(unittest.TestCase):
    def test_capture_keeps_containers_and_house_coverage_separate(self):
        from julius_gym.diagnostics import capture_outcome
        env = SimpleNamespace(get_food_supply=lambda: supply([storage(1, "granary", 500),
                              storage(2, "market", 80)]),
                              get_buildings=lambda: [{"food": 40, "population": 8}, {"food": 0, "population": 12}],
                              get_population_info=lambda: {"health": 33})
        observation = {key: SimpleNamespace(item=lambda value=value: value)
                       for key, value in (("population_total", 20), ("ratings_culture", 2), ("finance_treasury", 100))}
        self.assertEqual(capture_outcome(env, observation), {"population": 20, "culture": 2, "treasury": 100,
                         "health": 33, "residents_with_food": 8, "house_food_units": 40,
                         "granary_food_units": 500, "market_food_units": 80})

    def test_farm_progress_is_not_presented_as_inventory(self):
        from julius_gym.diagnostics import food_summary
        farm = {"id": 3, "kind": "farm", "x": 1, "y": 2, "workers": 10, "workers_required": 10,
                "road_access": 1, "progress_points": 175, "progress_max": 200}
        result = food_summary(supply([farm]), [])
        row = dict(zip(result["row_columns"], result["rows"][0]))
        self.assertIsNone(row["food_units"])
        self.assertIsNone(row["free_space_units"])
        self.assertEqual(row["progress_points"], 175)
        self.assertEqual(result["granary_food_units"], 0)

    def test_totals_do_not_confuse_free_space_with_food(self):
        from julius_gym.diagnostics import food_totals
        rows = [storage(1, "granary", 500), storage(2, "market", 80),
                {"id": 3, "kind": "farm", "progress_points": 175, "progress_max": 200}]
        self.assertEqual(food_totals(supply(rows)), {"granary_food_units": 500,
                         "market_food_units": 80, "granary_free_units": 1900})
        with self.assertRaises(ValueError):
            food_totals({"schema_version": 2, "units_per_load": 100, "buildings": []})

    def test_samples_are_bounded_but_totals_include_omitted_rows(self):
        from julius_gym.diagnostics import food_summary
        rows = [storage(i, "market", i) for i in range(1, 11)]
        result = food_summary(supply(rows), [{"food": 20}, {"food": 30}])
        self.assertEqual(result["market_food_units"], 55)
        self.assertEqual(result["house_food_units"], 50)
        self.assertEqual(len(result["rows"]), 4)
        self.assertEqual(result["rows_omitted"], 6)
        self.assertEqual(result["rows_total"], 10)

    def test_history_preserves_actual_deltas_and_only_four_cycles(self):
        from julius_gym.diagnostics import record_outcome
        before = {"population": 30, "health": 50, "market_food_units": 100}
        after = {"population": 25, "health": 52, "market_food_units": 20}
        history = []
        for i in range(6):
            prior = list(history)
            history = record_outcome(history, f"action_{i}", "failed" if i == 5 else "completed",
                                     17, before, after)
            self.assertEqual(len(prior), min(i, 4))
        self.assertEqual([r["candidate_id"] for r in history], [f"action_{i}" for i in range(2, 6)])
        self.assertEqual(history[-1]["delta"], {"population": -5, "health": 2, "market_food_units": -80})
        self.assertEqual(history[-1]["ticks"], 17)
        self.assertEqual(history[-1]["status"], "failed")
        self.assertEqual(before["population"], 30)

    def test_adapter_carries_food_and_observed_history(self):
        spec = importlib.util.spec_from_file_location("feedback_adapter", Path(__file__).parent / "examples/ollama_planner.py")
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        metrics = {key: i for i, key in enumerate(("population", "residents_with_food", "health", "culture",
                   "granary_food_units", "market_food_units", "house_food_units", "treasury"))}
        outcome = {"candidate_id": "wait", "status": "completed", "ticks": 800, "delta": metrics}
        context = {"decision_id": 1, "candidates": [{"id": "wait"}],
                   "food_supply": {"market_food_units": 200}, "recent_outcomes": [outcome] * 6}
        compact = json.loads(adapter.request_body(context, "test-model", 96)["prompt"])
        self.assertEqual(compact["food_supply"], context["food_supply"])
        self.assertEqual(len(compact["recent_outcomes"]), 4)
        row = dict(zip(compact["recent_columns"], compact["recent_outcomes"][0]))
        self.assertEqual(row["market_food_units_delta"], metrics["market_food_units"])
        self.assertEqual(row["ticks"], 800)


if __name__ == "__main__":
    unittest.main()
