"""Planner boundary tests; no licensed game data or local model needed."""

import sys
import subprocess
import unittest
import importlib.util
from pathlib import Path
from io import BytesIO, StringIO
from unittest.mock import patch
from unittest.mock import Mock
from julius_gym.planner import Candidate, command_choice, validate_choice, execute


class PlannerTests(unittest.TestCase):
    def test_observation_interval_stops_at_victory(self):
        from types import SimpleNamespace
        from julius_gym.planner import execute_cycle
        step = Mock(side_effect=[({}, 0, False, False, {"message": "Built housing"}),
                                 ({}, 100, True, False, {"message": "Victory achieved!"})])
        env = SimpleNamespace(step_at=step, get_victory_state=lambda: 1)
        candidate = Candidate("build", [(5, 1, 1)], "current", {})
        with patch("julius_gym.planner.fingerprint", return_value="current"):
            _, result, terminated, _ = execute_cycle(env, candidate, {}, 20, 10)
        self.assertTrue(terminated)
        self.assertEqual(result["status"], "won")
        self.assertEqual(step.call_count, 2)

    def test_observation_interval_charges_ticks_and_respects_budget(self):
        from types import SimpleNamespace
        from julius_gym.planner import execute_cycle
        env = SimpleNamespace(step_at=lambda *a: ({}, 0, False, False, {"message": "No action taken"}),
                              get_victory_state=lambda: 0)
        candidate = Candidate("test_wait", [(0, 0, 0)], "current", {})
        with patch("julius_gym.planner.fingerprint", return_value="current"):
            _, result, _, _ = execute_cycle(env, candidate, {}, 5, 3)
            self.assertEqual(result["candidate_id"], "test_wait")
            self.assertEqual((result["macro_ticks"], result["observation_ticks"], len(result["steps"])), (1, 2, 3))
            _, limited, _, _ = execute_cycle(env, candidate, {}, 2, 5)
            self.assertEqual(len(limited["steps"]), 2)
            self.assertEqual(limited["status"], "budget_exhausted")

    def test_bridge_not_offered_for_already_reachable_farmland(self):
        from julius_gym.planner import connect_if_needed
        make_bridge = Mock(return_value=[(55, 1, 1)])
        with self.assertRaisesRegex(RuntimeError, "already reachable"):
            connect_if_needed(lambda: [(35, 1, 1)], make_bridge)
        make_bridge.assert_not_called()
        self.assertEqual(connect_if_needed(Mock(side_effect=RuntimeError("no site")), make_bridge), [(55, 1, 1)])

    def test_local_api_request_is_bounded_and_constrained(self):
        spec = importlib.util.spec_from_file_location("ollama_adapter", Path(__file__).parent / "examples" / "ollama_planner.py")
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        body = adapter.request_body({"decision_id": 3, "state": {"buildings_housing_capacity": 80},
                                     "candidates": [{"id": "wait"}]}, "local-test", 96)
        self.assertFalse(body["stream"])
        self.assertFalse(body["think"])
        self.assertEqual(body["options"]["num_predict"], 96)
        self.assertEqual(body["format"]["properties"]["candidate_id"]["enum"], ["wait"])
        self.assertEqual(body["format"]["properties"]["decision_id"]["enum"], [3])
        import json
        self.assertEqual(json.loads(body["prompt"])["state"]["housing_capacity"], 80)

    def test_invalid_response_is_retained_for_review(self):
        audit = []
        with self.assertRaises(ValueError):
            command_choice([sys.executable, "-c", "print('malformed')"], self.context, audit=audit)
        self.assertEqual(audit[0]["stdout"].strip(), "malformed")

    def test_timeout_is_retained_for_review(self):
        audit = []
        with self.assertRaises(subprocess.TimeoutExpired):
            command_choice([sys.executable, "-c", "import time; time.sleep(2)"],
                           self.context, timeout=0.05, audit=audit)
        self.assertTrue(audit[0]["timed_out"])

    def test_local_api_adapter_round_trip(self):
        import json
        spec = importlib.util.spec_from_file_location("ollama_adapter", Path(__file__).parent / "examples" / "ollama_planner.py")
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        context = {"decision_id": 7, "candidates": [{"id": "wait"}]}
        response = {"done": True, "done_reason": "stop", "response": json.dumps(self.choice)}
        stdout = StringIO()
        with patch.object(sys, "argv", ["adapter", "--model", "local-test"]), \
                patch.object(sys, "stdin", StringIO(json.dumps(context))), \
                patch.object(sys, "stdout", stdout), patch.object(sys, "stderr", StringIO()), \
                patch.object(adapter.urllib.request, "urlopen", return_value=BytesIO(json.dumps(response).encode())):
            adapter.main()
        self.assertEqual(json.loads(stdout.getvalue()), self.choice)

    def test_terminal_preview_acceptance(self):
        from julius_gym.planner import preview_is_usable
        self.assertTrue(preview_is_usable({"status": "won"}))
        self.assertTrue(preview_is_usable({"status": "completed"}))
        for status in ("lost", "truncated", "failed", "terminated", "budget_exhausted"):
            self.assertFalse(preview_is_usable({"status": status}))

    def test_terminal_execution_distinguishes_win_and_loss(self):
        from types import SimpleNamespace
        for victory, expected in ((1, "won"), (-1, "lost")):
            env = SimpleNamespace(step_at=lambda *a: ({}, 100, True, False, {"message": "episode ended"}),
                                  get_victory_state=lambda: victory)
            candidate = Candidate("build", [(5, 1, 1)], "current", {})
            with patch("julius_gym.planner.fingerprint", return_value="current"):
                _, result, terminated, _ = execute(env, candidate, {}, 1)
            self.assertTrue(terminated)
            self.assertEqual(result["status"], expected)

    def setUp(self):
        self.context = {"decision_id": 7}
        self.candidates = {"wait": Candidate("wait", [(0, 0, 0)], "state", {})}
        self.choice = {"decision_id": 7, "candidate_id": "wait", "reason": "Observe effects"}

    def test_valid_choice(self):
        self.assertIs(validate_choice(self.choice, self.context, self.candidates), self.candidates["wait"])

    def test_rejects_stale_unknown_and_extra_fields(self):
        for change in ({"decision_id": 6}, {"candidate_id": "invented"},
                       {"python": "arbitrary code"}, {"decision_id": True}, {"reason": 42}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_choice({**self.choice, **change}, self.context, self.candidates)

    def test_local_command_round_trip(self):
        command = [sys.executable, "-c", "import json,sys; c=json.load(sys.stdin); print(json.dumps(dict(decision_id=c['decision_id'],candidate_id='wait',reason='test adapter')))" ]
        result = command_choice(command, self.context)
        self.assertIs(validate_choice(result, self.context, self.candidates), self.candidates["wait"])

    def test_failed_command_is_rejected(self):
        with self.assertRaises(ValueError):
            command_choice([sys.executable, "-c", "raise SystemExit(1)"], self.context)

    def test_non_json_command_is_rejected(self):
        with self.assertRaises(ValueError):
            command_choice([sys.executable, "-c", "print('not JSON')"], self.context)


if __name__ == "__main__":
    unittest.main()
