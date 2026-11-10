"""Provider configuration guards and explicit sampling parameters, no model service."""

import importlib.util
import json
from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("profile_adapter", Path(__file__).parent / "examples/ollama_planner.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class AdapterProfileTests(unittest.TestCase):
    def test_context_budget_only_changes_num_ctx_and_preserves_default(self):
        context = {"decision_id": 0, "candidates": [{"id": "wait"}]}
        default = adapter.request_body(context, "model", 256)
        self.assertEqual(default, adapter.request_body(context, "model", 256, context_tokens=4096))
        large = adapter.request_body(context, "model", 256, context_tokens=8192)
        self.assertEqual(large["options"]["num_ctx"], 8192)
        large["options"]["num_ctx"] = 4096
        self.assertEqual(default, large)

    def test_invalid_context_budget_rejected_before_inference(self):
        for value in ("2047", "16385", "0", "8192.5"):
            with patch.object(sys, "argv", ["adapter", "--model", "test-model", "--context-tokens", value]), \
                    patch.object(sys, "stderr", StringIO()) as error, \
                    patch.object(adapter.urllib.request, "urlopen") as request:
                with self.assertRaises(SystemExit) as stopped:
                    adapter.main()
                self.assertEqual(stopped.exception.code, 2)
                self.assertIn("context", error.getvalue())
                self.assertIn("invalid int" if "." in value else "2048..16384", error.getvalue())
                request.assert_not_called()

    def test_forecast_objects_preserve_fields_values_order_and_defaults(self):
        context = {"decision_id": 5, "forecast_policy": "no further construction", "candidates": [
            {"id": "first", "forecast": {"ticks": 1600, "status": "truncated", "population": 83,
                                        "culture": 15, "market_food_units": 172}},
            {"id": "second"}]}
        rows_body = adapter.request_body(context, "model", 256)
        explicit_rows = adapter.request_body(context, "model", 256, forecast_format="rows")
        self.assertEqual(rows_body, explicit_rows)
        objects_body = adapter.request_body(context, "model", 256, forecast_format="objects")
        rows, objects = json.loads(rows_body["prompt"]), json.loads(objects_body["prompt"])
        columns = rows.pop("forecast_columns")
        forecast_index = rows["candidate_columns"].index("forecast")
        self.assertNotIn("forecast_columns", objects)
        self.assertEqual([r[0] for r in objects["candidates"]], ["first", "second"])
        self.assertEqual(objects["candidates"][0][forecast_index]["status"], "truncated")
        self.assertEqual(objects["candidates"][0][forecast_index]["market_food_units"], 172)
        self.assertTrue(all(v is None for v in objects["candidates"][1][forecast_index].values()))
        for row in objects["candidates"]:
            self.assertEqual(list(row[forecast_index]), columns)
            row[forecast_index] = [row[forecast_index][key] for key in columns]
        self.assertEqual(rows, objects)
        self.assertEqual({k: v for k, v in rows_body.items() if k != "prompt"},
                         {k: v for k, v in objects_body.items() if k != "prompt"})

    def test_forecast_format_does_not_invent_forecasts(self):
        context = {"decision_id": 0, "candidates": [{"id": "wait"}]}
        rows = adapter.request_body(context, "model", 256)
        objects = adapter.request_body(context, "model", 256, forecast_format="objects")
        self.assertEqual(rows, objects)

    def test_forecast_format_cli_is_forwarded_and_audited(self):
        context = {"decision_id": 0, "forecast_policy": "test", "candidates": [
            {"id": "wait", "forecast": {"ticks": 800, "population": 12}}]}
        result = {"done": True, "done_reason": "stop", "response": json.dumps(
            {"decision_id": 0, "candidate_id": "wait", "reason": "test"})}
        for budget in (2048, 8192, 16384):
            with self.subTest(budget=budget), \
                    patch.object(sys, "argv", ["adapter", "--model", "test-model", "--forecast-format", "objects",
                                               "--context-tokens", str(budget)]), \
                    patch.object(sys, "stdin", StringIO(json.dumps(context))), \
                    patch.object(sys, "stdout", StringIO()) as output, \
                    patch.object(sys, "stderr", StringIO()) as audit, \
                    patch.object(adapter.urllib.request, "urlopen", return_value=StringIO(json.dumps(result))) as request:
                adapter.main()
            sent = json.loads(request.call_args.args[0].data)
            prompt = json.loads(sent["prompt"])
            self.assertEqual(prompt["candidates"][0][-1]["population"], 12)
            self.assertEqual(json.loads(output.getvalue())["candidate_id"], "wait")
            self.assertEqual(json.loads(audit.getvalue())["forecast_format"], "objects")
            self.assertEqual(sent["options"]["num_ctx"], budget)
            self.assertEqual(json.loads(audit.getvalue())["options"]["num_ctx"], budget)

    def test_explicit_sampling_preserves_model_and_schema_bounds(self):
        body = adapter.request_body({"decision_id": 3, "candidates": [{"id": "wait"}]}, "test-model", 256,
                                    temperature=0.7, top_p=0.8, top_k=20, min_p=0)
        self.assertEqual(body["options"], {"num_ctx": 4096, "num_predict": 256, "temperature": 0.7,
                                          "top_p": 0.8, "top_k": 20, "min_p": 0})
        self.assertEqual(body["format"]["properties"]["candidate_id"]["enum"], ["wait"])

    def test_known_thinking_only_tag_rejected_before_inference(self):
        with patch.object(sys, "argv", ["adapter", "--model", "qwen3:4b-thinking"]), \
                patch.object(sys, "stderr", StringIO()) as error, \
                patch.object(adapter.urllib.request, "urlopen") as request:
            with self.assertRaises(SystemExit) as stopped:
                adapter.main()
        self.assertEqual(stopped.exception.code, 2)
        self.assertIn("thinking-only", error.getvalue())
        request.assert_not_called()

    def test_invalid_sampling_rejected_before_inference(self):
        for flag, value in (("--temperature", "nan"), ("--top-p", "0"),
                            ("--top-k", "-1"), ("--min-p", "1.1")):
            with patch.object(sys, "argv", ["adapter", "--model", "test-model", flag, value]), \
                    patch.object(sys, "stderr", StringIO()) as error, \
                    patch.object(adapter.urllib.request, "urlopen") as request:
                with self.assertRaises(SystemExit):
                    adapter.main()
                self.assertIn("sampling", error.getvalue())
                request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
