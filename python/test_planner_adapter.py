"""Provider configuration guards and explicit sampling parameters, no model service."""

import importlib.util
from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("profile_adapter", Path(__file__).parent / "examples/ollama_planner.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class AdapterProfileTests(unittest.TestCase):
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
