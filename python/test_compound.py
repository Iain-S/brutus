"""Compound safety contracts, without native assets or a model service."""

from contextlib import contextmanager
import unittest
from unittest.mock import patch

import numpy as np

from julius_gym import compound
from julius_gym.planner import Candidate


class TinyEnv:
    """Ticked external-engine substitute; real execute/execute_cycle run unchanged."""

    def __init__(self):
        self.tick = 0
        self.actions = []
        self.end_at = None
        self.victory = 0
        self.fail_at = None
        self.raise_at = None

    def observation(self):
        return {"finance_treasury": np.array(100 - self.tick), "ratings_peace": np.array(self.tick)}

    def get_observation(self):
        return self.observation()

    def step_at(self, *action):
        self.tick += 1
        self.actions.append(action)
        if self.tick == self.raise_at:
            raise RuntimeError("engine exception")
        message = "Blocked" if self.tick == self.fail_at else "Built fixture"
        return self.observation(), 0.5, self.tick == self.end_at, False, {"message": message}

    def get_victory_state(self):
        return self.victory

    @contextmanager
    def snapshot(self):
        before = self.tick, list(self.actions)
        class Snapshot:
            def restore(snapshot):
                self.tick, self.actions = before[0], list(before[1])
        yield Snapshot()


class CompoundTests(unittest.TestCase):
    def setUp(self):
        self.env = TinyEnv()
        self.observation = self.env.observation()
        self.menus = []
        self.stale = False
        self.unavailable = False

        def menu(env, observation, mission, decision_id, budget, **kwargs):
            self.menus.append((env.tick, budget))
            name = "first" if env.tick == 0 else "future"
            state = "stale" if self.stale and env.tick else str(env.tick)
            candidates = {} if self.unavailable and env.tick else {
                name: Candidate(name, [(5, env.tick, 0)], state, {})}
            return {"unavailable": [{"id": "future", "reason": "blocked site"}]}, candidates

        self.patches = [patch("julius_gym.compound.decision_context", side_effect=menu),
                        patch("julius_gym.compound.fingerprint", side_effect=lambda e, o: str(e.tick)),
                        patch("julius_gym.planner.fingerprint", side_effect=lambda e, o: str(e.tick)),
                        patch("julius_gym.compound.forecast_state",
                              side_effect=lambda e, o, ticks, status: {"ticks": ticks, "status": status,
                                                                      "treasury": 100 - e.tick}),
                        patch("julius_gym.compound.native_diagnostics",
                              side_effect=lambda e: {"fixture_tick": e.tick})]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def plan(self, ids=("first", "future")):
        return compound.ShortPlan("0", ids)

    def preview(self, **kwargs):
        return compound.preview_short_plan(self.env, self.plan(), self.observation, {}, **kwargs)

    def test_proposal_schema_and_initial_membership(self):
        context = {"decision_id": 4}
        candidates = {"first": Candidate("first", [], "0", {})}
        proposal = {"decision_id": 4, "candidate_ids": ["first", "future"], "reason": "test"}
        plan = compound.validate_short_plan(proposal, context, candidates)
        self.assertEqual(plan, self.plan())
        for update in ({"decision_id": True}, {"decision_id": 3}, {"candidate_ids": []},
                       {"candidate_ids": ["first"] * 3}, {"candidate_ids": ["missing"]},
                       {"candidate_ids": ["first", candidates["first"]]},
                       {"candidate_ids": ["first", ""]}, {"candidate_ids": ["first", "x" * 129]},
                       {"reason": 1}, {"reason": "x" * 2001}, {"extra": 1}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                compound.validate_short_plan({**proposal, **update}, context, candidates)

    def test_resolves_future_only_after_first_cycle_and_charges_waits(self):
        result = self.preview(budget=10, minimum_ticks=3)
        self.assertEqual(self.menus, [(0, 10), (3, 7)])
        self.assertEqual(result["plan"]["ticks"], 6)
        self.assertEqual(result["control"]["ticks"], 6)
        self.assertTrue(result["equal_time"])
        self.assertTrue(result["plan"]["valid"])
        self.assertEqual([s["macro_ticks"] for s in result["plan"]["stages"]], [1, 1])
        self.assertEqual([s["observation_ticks"] for s in result["plan"]["stages"]], [2, 2])
        self.assertEqual([s["net_treasury_outlay"] for s in result["plan"]["stages"]], [3, 3])
        self.assertEqual(result["plan"]["stages"][1]["steps"][0]["action"], (5, 3, 0))
        self.assertEqual(result["plan"]["diagnostics"], {"fixture_tick": 6})
        self.assertEqual([s["diagnostics"] for s in result["plan"]["stages"]],
                         [{"fixture_tick": 3}, {"fixture_tick": 6}])
        self.assertEqual([s["after_observation"]["ratings_peace"] for s in result["plan"]["stages"]], [3, 6])
        self.assertEqual(self.env.tick, 0)
        self.assertEqual(self.env.actions, [])

    def test_invalid_successor_keeps_prefix_and_restores(self):
        self.unavailable = True
        result = self.preview(budget=10, minimum_ticks=3)
        self.assertEqual(result["plan"]["status"], "invalid_successor")
        self.assertFalse(result["plan"]["valid"])
        self.assertEqual(result["plan"]["ticks"], 3)
        self.assertEqual(result["control"]["ticks"], 3)
        self.assertFalse(result["plan"]["stages"][-1]["legal"])
        self.assertEqual(result["plan"]["stages"][-1]["reason"], "blocked site")
        self.assertEqual(self.env.tick, 0)

    def test_stale_future_never_executes_and_restores(self):
        self.stale = True
        with self.assertRaisesRegex(ValueError, "Stale candidate"):
            self.preview(budget=10, minimum_ticks=3)
        self.assertEqual(self.env.tick, 0)

    def test_stale_plan_rejected_before_simulation(self):
        self.env.tick = 1
        with self.assertRaisesRegex(ValueError, "Stale plan"):
            self.preview(budget=10)
        self.assertEqual(self.env.tick, 1)

    def test_stale_observation_rejected_even_with_matching_live_identity(self):
        stale = {**self.observation, "finance_treasury": np.array(999)}
        with self.assertRaisesRegex(ValueError, "Stale observation"):
            compound.preview_short_plan(self.env, self.plan(), stale, {}, 10)
        self.assertEqual(self.env.tick, 0)
        self.assertEqual(self.menus, [])

    def test_read_only_observation_propagates_native_failure(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from julius_gym import JuliusEnv
        env = object.__new__(JuliusEnv)
        env.env_handle = None
        env.lib = SimpleNamespace(julius_env_get_observation=Mock(return_value=-1))
        with self.assertRaisesRegex(RuntimeError, "observation"):
            env.get_observation()

    def test_native_evidence_script_refuses_disabled_assertions(self):
        from pathlib import Path
        import subprocess
        import sys
        result = subprocess.run([sys.executable, "-O", str(Path(__file__).with_name("test_compound_engine.py")),
                                 "--data-dir", "unused", "--lib-path", "unused"],
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires assertions", result.stderr)

    def test_budget_exhaustion_never_resolves_second_step(self):
        result = self.preview(budget=2, minimum_ticks=3)
        self.assertEqual(self.menus, [(0, 2)])
        self.assertEqual(result["plan"]["status"], "budget_exhausted")
        self.assertEqual(result["plan"]["ticks"], 2)
        self.assertEqual(result["control"]["ticks"], 2)
        self.assertFalse(result["plan"]["valid"])

    def test_exact_cycle_budget_still_leaves_unexecuted_plan(self):
        result = self.preview(budget=3, minimum_ticks=3)
        self.assertEqual(result["plan"]["status"], "budget_exhausted")
        self.assertEqual(len(result["plan"]["stages"]), 1)

    def test_terminal_states_stop_and_restore(self):
        for victory, status in ((1, "won"), (-1, "lost"), (0, "terminated")):
            with self.subTest(status=status):
                self.env.end_at, self.env.victory = 2, victory
                result = self.preview(budget=10, minimum_ticks=3)
                self.assertEqual(result["plan"]["status"], status)
                self.assertEqual(result["plan"]["ticks"], 2)
                self.assertEqual(len(result["plan"]["stages"]), 1)
                self.assertEqual(self.env.tick, 0)

    def test_failed_construction_does_not_observe_or_resolve_successor(self):
        self.env.fail_at = 1
        result = self.preview(budget=10, minimum_ticks=3)
        self.assertEqual(result["plan"]["status"], "failed")
        self.assertEqual(result["plan"]["ticks"], 1)
        self.assertEqual(len(result["plan"]["stages"]), 1)
        self.assertFalse(result["plan"]["valid"])
        self.assertEqual(self.env.tick, 0)

    def test_exception_in_execution_or_control_restores(self):
        self.env.raise_at = 2
        with self.assertRaisesRegex(RuntimeError, "engine exception"):
            self.preview(budget=10, minimum_ticks=3)
        self.assertEqual(self.env.tick, 0)
        self.env.raise_at = None
        with patch("julius_gym.compound.native_diagnostics", side_effect=[{}, {}, {}, RuntimeError("control")]):
            with self.assertRaisesRegex(RuntimeError, "control"):
                self.preview(budget=10, minimum_ticks=3)
        self.assertEqual(self.env.tick, 0)

    def test_exception_regenerating_successor_restores(self):
        original = compound.decision_context
        def menu(*args, **kwargs):
            if self.env.tick:
                raise RuntimeError("successor generation")
            return original(*args, **kwargs)
        with patch("julius_gym.compound.decision_context", side_effect=menu):
            with self.assertRaisesRegex(RuntimeError, "successor generation"):
                self.preview(budget=10, minimum_ticks=3)
        self.assertEqual(self.env.tick, 0)

    def test_control_early_terminal_is_not_equal_time(self):
        original = self.env.step_at
        def step(*action):
            obs, reward, _, truncated, info = original(*action)
            return obs, reward, action[0] == 0 and self.env.tick == 1, truncated, info
        self.env.step_at = step
        result = self.preview(budget=10, minimum_ticks=0)
        self.assertEqual(result["plan"]["ticks"], 2)
        self.assertEqual(result["control"]["ticks"], 1)
        self.assertFalse(result["equal_time"])
        self.assertEqual(self.env.tick, 0)

    def test_partial_macro_is_retained_but_invalid(self):
        def menu(env, observation, mission, decision_id, budget, **kwargs):
            return {}, {"first": Candidate("first", [(5, 0, 0)] * 3, "0", {})}
        with patch("julius_gym.compound.decision_context", side_effect=menu):
            result = self.preview(budget=2, minimum_ticks=0)
        self.assertEqual(result["plan"]["status"], "budget_exhausted")
        self.assertEqual(result["plan"]["ticks"], 2)
        self.assertEqual(result["plan"]["stages"][0]["macro_ticks"], 2)
        self.assertFalse(result["plan"]["valid"])
        self.assertEqual(self.env.tick, 0)

    def test_single_step_and_zero_tick_invalid_initial(self):
        result = compound.preview_short_plan(self.env, self.plan(("first",)), self.observation,
                                             {}, 3, minimum_ticks=3)
        self.assertEqual(result["plan"]["status"], "completed")
        self.assertTrue(result["plan"]["valid"])
        result = compound.preview_short_plan(self.env, self.plan(("missing",)), self.observation,
                                             {}, 3, minimum_ticks=3)
        self.assertEqual(result["plan"]["status"], "invalid_initial")
        self.assertEqual(result["plan"]["ticks"], 0)
        self.assertEqual(result["control"]["ticks"], 0)
        self.assertFalse(result["plan"]["valid"])
        self.assertEqual(self.env.tick, 0)

    def test_truncation_stops_successor_resolution(self):
        original = self.env.step_at
        def step(*action):
            obs, reward, terminated, _, info = original(*action)
            return obs, reward, terminated, self.env.tick == 2, info
        self.env.step_at = step
        result = self.preview(budget=10, minimum_ticks=3)
        self.assertEqual(result["plan"]["status"], "truncated")
        self.assertEqual(result["plan"]["ticks"], 2)
        self.assertFalse(result["plan"]["valid"])
        self.assertEqual(self.menus, [(0, 10)])
        self.assertEqual(self.env.tick, 0)

    def test_bounds_rejected_before_snapshot(self):
        for kwargs in ({"budget": 0}, {"budget": 8001}, {"budget": True},
                       {"budget": 10, "minimum_ticks": -1}, {"budget": 10, "minimum_ticks": 801}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.preview(**kwargs)
        for ids in ((), ("first",) * 3, (Candidate("first", [], "0", {}),)):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                compound.preview_short_plan(self.env, self.plan(ids), self.observation, {}, 10)


if __name__ == "__main__":
    unittest.main()
