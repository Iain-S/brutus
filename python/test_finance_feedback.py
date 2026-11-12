"""Taxation tools and factual finance feedback without game assets."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from julius_gym.env import ActionType as A, JuliusEnv
from julius_gym.planner import Candidate, execute, proposals
from julius_gym import diagnostics


class FinanceFeedbackTests(unittest.TestCase):
    def test_binding_grows_buffer_and_rejects_closed_handles(self):
        env = object.__new__(JuliusEnv)
        env.env_handle = 1
        def read(handle, output, capacity):
            if capacity < 128 * 1024:
                return -1
            output.value = b'{"treasury":123}'
            return 0
        query = Mock(side_effect=read)
        env.lib = SimpleNamespace(julius_env_get_finance_state=query)
        try:
            self.assertEqual(env.get_finance_state(), {"treasury": 123})
            self.assertEqual(query.call_count, 2)
            env.env_handle = None
            query.reset_mock()
            with self.assertRaisesRegex(RuntimeError, "finance"):
                env.get_finance_state()
            query.assert_not_called()
        finally:
            env.env_handle = None

    def test_binding_failure_is_bounded(self):
        env = object.__new__(JuliusEnv)
        env.env_handle = 1
        env.lib = SimpleNamespace(julius_env_get_finance_state=Mock(return_value=-1))
        try:
            with self.assertRaisesRegex(RuntimeError, "8 MiB"):
                env.get_finance_state()
            self.assertEqual(env.lib.julius_env_get_finance_state.call_count, 8)
        finally:
            env.env_handle = None

    def test_summary_retains_accounting_but_bounds_collectors(self):
        state = {"treasury": 100, "yearly_collected_denarii": 7,
                 "monthly_tax_base_units": {"collected_plebs": 200},
                 "houses": [{"id": i} for i in range(20)],
                 "collectors": [{"id": i} for i in range(12, 0, -1)]}
        summary = diagnostics.finance_summary(state)
        self.assertNotIn("houses", summary)
        self.assertEqual(summary["yearly_collected_denarii"], 7)
        self.assertEqual(summary["monthly_tax_base_units"], state["monthly_tax_base_units"])
        self.assertEqual([r["id"] for r in summary["collectors"]], list(range(1, 9)))
        self.assertEqual(summary["collectors_total"], 12)
        self.assertEqual(summary["collectors_omitted"], 4)
        self.assertEqual(len(state["collectors"]), 12)

    def test_forum_and_rate_wage_choices_are_optional_existing_actions(self):
        env = SimpleNamespace(get_map_data=lambda: (None, None, 10, 10),
                              get_buildings=lambda: [{"type": 92, "x": 2, "y": 2}],
                              get_housing_state=lambda: {"garden_model": {"desirability_range": 4}})
        with patch("julius_gym.planner.exclude_hazard", return_value=None), \
                patch("julius_gym.planner.building_plan", return_value=[]) as plan:
            choices = dict(proposals(env, {"entry": (0, 0), "earthquake": {}}, 14))
            choices["add_forum_district_0"]()
            self.assertEqual(plan.call_args.args[-2:], (A.BUILD_FORUM, 2))
            for name, kind in (("tax_up", A.ADJUST_TAX_UP), ("tax_down", A.ADJUST_TAX_DOWN),
                               ("wages_up", A.ADJUST_WAGES_UP), ("wages_down", A.ADJUST_WAGES_DOWN)):
                self.assertEqual(choices["adjust_" + name](), [(kind, 0, 0)])

    def test_executor_rejects_native_control_limits(self):
        for kind, success, failure in (
                (A.ADJUST_TAX_UP, "Tax increased by 1%", "Tax already at maximum (25%)"),
                (A.ADJUST_TAX_DOWN, "Tax decreased by 1%", "Tax already at minimum (0%)"),
                (A.ADJUST_WAGES_UP, "Wages increased", "Wages already at maximum"),
                (A.ADJUST_WAGES_DOWN, "Wages decreased", "Wages already at minimum")):
            for message, status in ((success, "completed"), (failure, "failed")):
                env = SimpleNamespace(step_at=Mock(return_value=({}, 0, False, False, {"message": message})))
                with patch("julius_gym.planner.fingerprint", return_value="current"):
                    _, result, _, _ = execute(env, Candidate("rate", [(kind, 0, 0)], "current", {}), {}, 1)
                self.assertEqual(result["status"], status, message)

    def test_provider_retains_finance_scope(self):
        spec = importlib.util.spec_from_file_location("finance_adapter", Path(__file__).parent / "examples/ollama_planner.py")
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        context = {"decision_id": 0, "finance": {"yearly_collected_denarii": 7},
                   "candidates": [{"id": "wait"}]}
        prompt = json.loads(adapter.request_body(context, "model", 256)["prompt"])
        self.assertEqual(prompt["finance"], context["finance"])


if __name__ == "__main__":
    unittest.main()
