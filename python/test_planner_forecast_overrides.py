"""Lossless forecast packing preserves all choices, scalar types and legacy requests."""

import copy
import hashlib
import importlib.util
from io import StringIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("override_adapter", Path(__file__).parent / "examples/ollama_planner.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class ForecastOverrideTests(unittest.TestCase):
    def context(self):
        return {"decision_id": 3, "forecast_policy": "test", "candidates": [
            {"id": "wait", "forecast": {"population": 44, "treasury": 7655}},
            {"id": "expand_housing", "forecast": {"population": 72, "treasury": 7478}}]}

    def assert_roundtrip(self, context, reason_first=False):
        before = copy.deepcopy(context)
        options = dict(reason_first=reason_first, context_tokens=8192, temperature=.7, top_p=.8, top_k=20, min_p=0.)
        full = adapter.request_body(context, "model", 256, forecast_format="objects", **options)
        body = adapter.request_body(context, "model", 256, forecast_format="overrides", **options)
        packed = json.loads(body["prompt"])
        self.assertNotIn("forecast_columns", packed)
        baseline = packed.pop("forecast_baseline")
        semantics = packed.pop("forecast_semantics")
        self.assertIn("Absolute values", semantics)
        self.assertIn("not zero", semantics)
        self.assertIn("Null means unknown", semantics)
        self.assertEqual([row[0] for row in packed["candidates"]], [c["id"] for c in context["candidates"]])
        index = packed["candidate_columns"].index("forecast")
        encoded_rows = copy.deepcopy(packed["candidates"])
        for row in packed["candidates"]:
            row[index] = {**baseline["forecast"], **row[index]}
        # JSON equality also distinguishes false/0, true/1, floats/ints and nulls.
        self.assertEqual(json.dumps(packed), full["prompt"])
        self.assertEqual({k: v for k, v in body.items() if k != "prompt"},
                         {k: v for k, v in full.items() if k != "prompt"})
        self.assertEqual(context, before)
        return baseline, encoded_rows, index

    def test_preserves_every_candidate_and_nonforecast_field_for_both_reason_profiles(self):
        context = self.context()
        context.update(imperial={"personal_savings": 70}, housing={"rows_omitted": 10},
                       finance={"treasury": 8000}, recent_outcomes=[])
        context["candidates"].insert(0, {"id": "send_gift", "ticks": 1, "benefit": "native gift",
                                          "personal_savings_cost": 50, "forecast": {"population": 44, "favor": 53}})
        for reason in (False, True):
            baseline, rows, index = self.assert_roundtrip(context, reason)
            self.assertEqual(baseline["candidate_id"], "wait")
            self.assertEqual(rows[1][index], {})
            self.assertEqual(rows[2][index], {"population": 72, "treasury": 7478})

    def test_nulls_and_missing_forecasts_do_not_become_zero(self):
        context = self.context()
        context["candidates"].append({"id": "unknown"})
        baseline, rows, index = self.assert_roundtrip(context)
        self.assertEqual(rows[-1][index]["population"], None)
        self.assertEqual(rows[-1][index]["treasury"], None)
        self.assertIsNone(baseline["forecast"]["culture"])

    def test_equal_numbers_with_different_scalar_types_are_not_elided(self):
        context = self.context()
        context["candidates"][0]["forecast"].update(population=0, farm_workers=1, health=0.0, treasury=False)
        context["candidates"][1]["forecast"].update(population=False, farm_workers=True, health=0, treasury=0)
        _, rows, index = self.assert_roundtrip(context)
        for key in ("population", "farm_workers", "health", "treasury"):
            self.assertIn(key, rows[1][index])

    def test_individual_time_and_status_are_preserved(self):
        context = self.context()
        context["candidates"][0]["forecast"].update(ticks=1600, status="completed")
        context["candidates"][1]["forecast"].update(ticks=200, status="won")
        context["candidates"].append({"id": "short", "forecast": {"ticks": 400, "status": "truncated"}})
        _, rows, index = self.assert_roundtrip(context)
        self.assertEqual(rows[1][index]["ticks"], 200)
        self.assertEqual(rows[2][index]["status"], "truncated")

    def test_signed_float_zero_is_not_elided_as_numeric_equality(self):
        context = self.context()
        context["candidates"][0]["forecast"].update(health=-0.0, farm_workers=0.0)
        context["candidates"][1]["forecast"].update(health=0.0, farm_workers=-0.0)
        _, rows, index = self.assert_roundtrip(context)
        self.assertIn("health", rows[1][index])
        self.assertIn("farm_workers", rows[1][index])

    def test_missing_wait_uses_empty_baseline_and_full_named_forecasts(self):
        context = self.context()
        context["candidates"].pop(0)
        baseline, rows, index = self.assert_roundtrip(context)
        self.assertEqual(baseline, {"candidate_id": None, "forecast": {}})
        self.assertEqual(len(rows[0][index]), 20)

    def test_empty_candidates_and_unknown_wait_are_honest(self):
        context = self.context()
        context["candidates"] = []
        baseline, rows, _ = self.assert_roundtrip(context)
        self.assertEqual(baseline, {"candidate_id": None, "forecast": {}})
        self.assertEqual(rows, [])
        context["candidates"] = [{"id": "wait"}]
        baseline, rows, index = self.assert_roundtrip(context)
        self.assertTrue(all(value is None for value in baseline["forecast"].values()))
        self.assertEqual(rows[0][index], {})

    def test_disabled_forecasts_emit_no_encoding(self):
        context = self.context()
        del context["forecast_policy"]
        packed = adapter.request_body(context, "model", 256, forecast_format="overrides")
        self.assertEqual(json.dumps(packed), json.dumps(adapter.request_body(context, "model", 256)))

    def test_existing_request_bytes_are_frozen_for_both_formats_and_profiles(self):
        expected = {
            ("rows", False): "d703f2b06a5c49660efa477f1c9c4714d08ed4fd3778c5a0229c894477713cc2",
            ("rows", True): "c9e5f4573d19aa76a1af2103bce5df1794e28d81124df0f5094ac66775d61edc",
            ("objects", False): "73502d754dba23199d3d56cca46469561f4ef44a1d5fa033af5b41aa6de93c1e",
            ("objects", True): "675126e6f9f55c75cfeaa1f511d9a1ed879bcf1029501f8b9f88bcd4507de8df"}
        for (fmt, reason), digest in expected.items():
            body = adapter.request_body(self.context(), "model", 256, forecast_format=fmt,
                                        reason_first=reason, context_tokens=8192)
            self.assertEqual(hashlib.sha256(json.dumps(body).encode()).hexdigest(), digest)

    def test_cli_forwards_encoding_and_keeps_validation(self):
        for unsafe in (False, True):
            result = {"done": True, "done_reason": "stop", "prompt_eval_count": 4000 if unsafe else 128,
                      "response": json.dumps({"decision_id": 3, "candidate_id": "wait", "reason": "model text"})}
            with patch.object(sys, "argv", ["adapter", "--model", "model", "--forecast-format", "overrides", "--reason-first"]), \
                    patch.object(sys, "stdin", StringIO(json.dumps(self.context()))), \
                    patch.object(sys, "stdout", StringIO()) as output, \
                    patch.object(sys, "stderr", StringIO()) as audit, \
                    patch.object(adapter.urllib.request, "urlopen", return_value=StringIO(json.dumps(result))) as request:
                if unsafe:
                    with self.assertRaisesRegex(RuntimeError, "context headroom"):
                        adapter.main()
                    self.assertEqual(output.getvalue(), "")
                else:
                    adapter.main()
                    self.assertEqual(json.loads(output.getvalue())["candidate_id"], "wait")
            body = json.loads(request.call_args.args[0].data)
            self.assertIn("forecast_baseline", json.loads(body["prompt"]))
            metadata = json.loads(audit.getvalue())
            self.assertEqual(metadata["forecast_format"], "overrides")
            self.assertTrue(metadata["reason_first"])


if __name__ == "__main__":
    unittest.main()
