"""Compound runner boundaries; native delivery is tested separately."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / "examples"))
import run_compound_planner as runner


class RunnerTests(unittest.TestCase):
    def test_rejected_first_proposal_keeps_error_audit_and_never_executes(self):
        from types import SimpleNamespace
        from julius_gym.planner import Candidate
        context = {"decision_id": 0, "candidates": [{"id": "wait"}]}
        class BadModel:
            def call(self, stage, body, validate):
                answer = {"decision_id": 0, "candidate_id": "invented", "reason": "test"}
                validate(answer)
                return answer
        actions = []
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "decision"
            with patch.object(runner, "fingerprint", return_value="initial"), \
                 patch.object(runner, "decision_context", return_value=(
                     context, {"wait": Candidate("wait", [], "initial", {})})):
                with self.assertRaises(ValueError):
                    runner.run_decision(SimpleNamespace(), {}, {}, 0, 8000, directory, BadModel(), actions.append)
            audit = json.loads((directory / "decision.json").read_text())
            self.assertEqual(audit["status"], "error")
            self.assertFalse(audit["execution_verified"])
            self.assertEqual(actions, [])
            self.assertFalse((directory / "actual.json").exists())

    def test_delivery_refuses_changed_trace_endpoint_and_diagnostics(self):
        expected = {"steps": [{"action": [0, 0, 0], "message": "idle", "reward": 0.}],
                    "ticks": 1, "status": "completed", "valid": True,
                    "observation": {"ratings_peace": 7}, "forecast": {"ticks": 1},
                    "diagnostics": {"finance": {"treasury": 90}}}
        runner.verify_delivery(expected, copy.deepcopy(expected))
        for key, replacement in (("steps", []), ("ticks", 2), ("status", "truncated"),
                                 ("observation", {"ratings_peace": 8}),
                                 ("diagnostics", {"finance": {"treasury": 91}})):
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                runner.verify_delivery(expected, {**expected, key: replacement})

    def test_cli_rejects_unbounded_decisions_before_native_initialization(self):
        for value in ("0", "5"):
            result = subprocess.run([sys.executable, str(Path(runner.__file__)), "--data-dir", "unused",
                                     "--lib-path", "unused", "--max-decisions", value],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("max-decisions must be 1..4", result.stderr)

    def test_finalization_preserves_primary_error_despite_damaged_audit(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            child = directory / "decision-00"
            child.mkdir()
            (child / "first.audit.json").write_text("{truncated")
            artifacts = SimpleNamespace(directory=directory, ready=True, metadata={}, finish=Mock())
            env = SimpleNamespace(get_observation=Mock(side_effect=RuntimeError("diagnostic failed")),
                                  close=Mock())
            primary = RuntimeError("primary failure")
            runner.finalize(artifacts, env, 10, 0, primary)
            self.assertTrue(env.close.called)
            summary = artifacts.finish.call_args.args[1]
            self.assertIs(artifacts.finish.call_args.args[2], primary)
            self.assertIsNone(summary["api_calls"])
            self.assertEqual(summary["ticks"], 10)
            self.assertTrue(artifacts.metadata["finalization_errors"])


if __name__ == "__main__":
    unittest.main()
