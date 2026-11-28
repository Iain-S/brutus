"""Opt-in reason-first requests preserve facts, legal choices and validation."""

import importlib.util
from io import StringIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("reason_adapter", Path(__file__).parent / "examples/ollama_planner.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class ReasonFirstTests(unittest.TestCase):
    def context(self):
        return {"decision_id": 3, "forecast_policy": "test", "candidates": [
            {"id": "wait", "forecast": {"population": 44, "treasury": 7655}},
            {"id": "expand_housing", "forecast": {"population": 72, "treasury": 7478}}]}

    def test_default_serialization_is_unchanged(self):
        default = adapter.request_body(self.context(), "model", 256)
        explicit = adapter.request_body(self.context(), "model", 256, reason_first=False)
        self.assertEqual(json.dumps(default), json.dumps(explicit))
        self.assertEqual(list(default["format"]["properties"]), ["decision_id", "candidate_id", "reason"])
        self.assertIn("under eight words", default["system"])

    def test_opt_in_orders_reason_without_changing_facts_choices_or_options(self):
        for forecast_format in ("rows", "objects"):
            with self.subTest(forecast_format=forecast_format):
                options = dict(temperature=0.7, top_p=0.8, top_k=20, min_p=0,
                               forecast_format=forecast_format, context_tokens=8192)
                default = adapter.request_body(self.context(), "model", 256, **options)
                reason = adapter.request_body(self.context(), "model", 256, reason_first=True, **options)
                self.assertEqual(list(reason["format"]["properties"]), ["reason", "decision_id", "candidate_id"])
                self.assertEqual(reason["format"]["required"], ["reason", "decision_id", "candidate_id"])
                self.assertEqual(reason["format"]["properties"], default["format"]["properties"])
                self.assertFalse(reason["format"]["additionalProperties"])
                self.assertEqual(reason["format"]["properties"]["candidate_id"]["enum"], ["wait", "expand_housing"])
                self.assertIn("compare at least two", reason["system"])
                self.assertIn("under 100 words", reason["system"])
                self.assertNotIn("under eight words", reason["system"])
                self.assertEqual({k: v for k, v in reason.items() if k not in ("system", "format")},
                                 {k: v for k, v in default.items() if k not in ("system", "format")})

    def run_cli(self, enabled, *, prompt_tokens=128):
        choice = {"reason": "Unverified model rationale", "decision_id": 3, "candidate_id": "wait"}
        result = {"done": True, "done_reason": "stop", "prompt_eval_count": prompt_tokens,
                  "response": json.dumps(choice)}
        argv = ["adapter", "--model", "test-model"] + (["--reason-first"] if enabled else [])
        with patch.object(sys, "argv", argv), \
                patch.object(sys, "stdin", StringIO(json.dumps(self.context()))), \
                patch.object(sys, "stdout", StringIO()) as output, \
                patch.object(sys, "stderr", StringIO()) as audit, \
                patch.object(adapter.urllib.request, "urlopen", return_value=StringIO(json.dumps(result))) as request:
            if prompt_tokens == 4000:
                with self.assertRaisesRegex(RuntimeError, "context headroom"):
                    adapter.main()
                self.assertEqual(output.getvalue(), "")
            else:
                adapter.main()
                self.assertEqual(json.loads(output.getvalue()), choice)
        return json.loads(request.call_args.args[0].data), json.loads(audit.getvalue())

    def test_cli_forwards_and_audits_both_profiles(self):
        for enabled in (False, True):
            with self.subTest(enabled=enabled):
                body, audit = self.run_cli(enabled)
                self.assertEqual(audit["reason_first"], enabled)
                self.assertEqual(list(body["format"]["properties"])[0], "reason" if enabled else "decision_id")

    def test_reason_first_still_rejects_unsafe_headroom_and_audits_profile(self):
        _, audit = self.run_cli(True, prompt_tokens=4000)
        self.assertTrue(audit["reason_first"])
        self.assertEqual(audit["prompt_eval_count"], 4000)


if __name__ == "__main__":
    unittest.main()
