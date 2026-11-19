"""Bounded native housing feedback, optional garden geometry and buffer growth."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np

from julius_gym.diagnostics import housing_summary, housing_totals
from julius_gym.env import ActionType as A, JuliusEnv
from julius_gym.housing import garden_plan


class HousingFeedbackTests(unittest.TestCase):
    def state(self):
        houses = [{"id": i, "population": 7, "level": 1, "next_level": 2,
                   "desirability_cached": -6, "desirability_allows_upgrade": False,
                   "current_goods_services_pass": True, "next_goods_services_pass": True,
                   "inventory_units": [28, 0, 0, 0, 0, 0, 0, 0]} for i in range(12)]
        houses.append({**houses[0], "id": 20, "population": 0})
        return {"houses": houses, "models": [{"level": i, "water": 1} for i in range(3)],
                "native_cached_prosperity_cap": 10, "multiple_wine_available": False,
                "garden_model": {"desirability_range": 4}}

    def test_housing_summary_uses_all_totals_but_bounds_rows(self):
        state = self.state()
        summary = housing_summary(state)
        self.assertEqual(summary["occupied_houses"], 12)
        self.assertEqual(summary["desirability_blocked_houses"], 12)
        self.assertEqual(summary["rows_total"], 13)
        self.assertEqual(len(summary["rows"]), 8)
        self.assertEqual(summary["rows_omitted"], 5)
        self.assertEqual([m["level"] for m in summary["models"]], [1, 2])
        self.assertEqual(summary["next_goods_services_failed_houses"], 0)

    def test_maximum_level_is_not_a_failed_upgrade(self):
        state = self.state()
        state["houses"] = [{**state["houses"][0], "level": 19, "next_level": None,
                            "next_goods_services_pass": None}]
        totals = housing_totals(state)
        self.assertEqual(totals["desirability_blocked_houses"], 0)
        self.assertEqual(totals["next_goods_services_failed_houses"], 0)

    def test_gardens_need_no_roads_and_preserve_infrastructure(self):
        terrain = np.zeros((12, 12), dtype=np.uint16)
        buildings = np.zeros((12, 12), dtype=np.int32)
        terrain[5, 4] = 0x40
        terrain[4, 5] = 4
        buildings[5, 5] = 1
        actions = garden_plan(terrain, buildings, 12, 12, (5, 5), radius=2)
        planted = [(x, y) for kind, x, y in actions if kind == A.BUILD_GARDEN]
        self.assertEqual(len(planted), 4)
        self.assertFalse(any(kind == A.BUILD_ROAD for kind, _, _ in actions))
        self.assertFalse(set(planted) & {(4, 5), (5, 4), (5, 5)})
        self.assertTrue(all(max(abs(x - 5), abs(y - 5)) <= 2 for x, y in planted))

    def test_garden_clearing_is_explicit_and_no_space_is_reported(self):
        terrain = np.full((9, 9), 2, dtype=np.uint16)
        buildings = np.zeros((9, 9), dtype=np.int32)
        terrain[4, 4] = 1
        self.assertEqual(garden_plan(terrain, buildings, 9, 9, (4, 4)),
                         [(A.CLEAR_LAND, 4, 4), (A.BUILD_GARDEN, 4, 4)])
        terrain[4, 4] = 0x100
        with self.assertRaisesRegex(RuntimeError, "garden"):
            garden_plan(terrain, buildings, 9, 9, (4, 4))

    def test_housing_binding_grows_buffer_without_partial_data(self):
        calls = []
        def read(handle, output, capacity):
            calls.append(capacity)
            if capacity < 128 * 1024:
                return -1
            output.value = b'{"houses":[],"models":[]}'
            return 0
        env = object.__new__(JuliusEnv)
        env.env_handle = 1
        env.lib = SimpleNamespace(julius_env_get_housing_state=Mock(side_effect=read))
        try:
            self.assertEqual(env.get_housing_state(), {"houses": [], "models": []})
            self.assertEqual(calls, [64 * 1024, 128 * 1024])
        finally:
            env.env_handle = None

    def test_housing_binding_stops_on_failure_and_rejects_closed_handles(self):
        env = object.__new__(JuliusEnv)
        env.env_handle = 1
        query = Mock(return_value=-1)
        env.lib = SimpleNamespace(julius_env_get_housing_state=query)
        try:
            with self.assertRaisesRegex(RuntimeError, "8 MiB"):
                env.get_housing_state()
            self.assertEqual(query.call_count, 8)
            self.assertEqual(query.call_args.args[-1], 8 * 1024 * 1024)
            env.env_handle = None
            query.reset_mock()
            with self.assertRaisesRegex(RuntimeError, "housing"):
                env.get_housing_state()
            query.assert_not_called()
        finally:
            env.env_handle = None


if __name__ == "__main__":
    unittest.main()
