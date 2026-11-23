"""Frozen channel intervention and strict evidence lifecycle without inference."""

import copy
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / "examples"))
import compound_planner as protocol
import probe_compound_capability as capability
import probe_compound_channel as channel
import test_compound_capability as fixtures


class ChannelTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.CapabilityTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.reference = self.fixture.reference
        self.directory = self.fixture.fixture.root / "channel"

    def test_request_changes_only_format_and_does_not_mutate_input(self):
        data = capability.load_reference(self.reference)[3]
        base = copy.deepcopy(data["base_request"])
        schema = channel.request(base, True)
        plain = channel.request(base, False)
        self.assertEqual(schema, capability.profile_request(base, ("compound", "single", "wait"), "thinking"))
        removed = schema.pop("format")
        self.assertIsInstance(removed, dict)
        self.assertEqual(schema, plain)
        self.assertEqual(base, data["base_request"])

    def execute(self, mode="normal"):
        calls, checks = [], []
        def transport(request_path, raw_path, status_path, timeout):
            body = json.loads(Path(request_path).read_text())
            calls.append(body)
            if mode == "timeout":
                raise TimeoutError("fixture transport deadline")
            result = {"model": capability.THINK_MODEL, "done": True, "done_reason": "stop",
                      "prompt_eval_count": 5800, "eval_count": 25, "thinking": "unverified trace",
                      "response": json.dumps({"decision_id": 3, "candidate_id": "wait"})}
            if "format" in body:
                result.update(thinking=result["response"], response="")
            Path(raw_path).write_bytes(json.dumps(result).encode())
            protocol.write_json(status_path, {"http_status": 200, "body_complete": True})
        def metadata():
            checks.append(True)
            value = {"server_version": "0.16.2"}
            for name, profile in capability.PROFILES.items():
                value[name] = {"model": profile["model"], "digest": profile["digest"], "show": {
                    "template": "fixture", "parameters": "top_p 0.8", "model_info": {"count": 4},
                    "capabilities": ["completion", "thinking"]}}
            if len(checks) == 2:
                if mode == "identity": value["thinking"]["digest"] = "changed"
                if mode == "receipt":
                    (self.directory / "call-01" / "selection.http.json").unlink()
            return value
        with patch.object(protocol, "run_transport", side_effect=transport), \
             patch.object(capability, "model_metadata", side_effect=metadata), \
             patch("julius_gym.JuliusEnv.__init__", side_effect=AssertionError("No native actions")), \
             redirect_stdout(StringIO()):
            channel.run_probe(self.reference, self.directory)
        return calls, json.loads((self.directory / "manifest.json").read_text())

    def test_abba_rejects_wrong_channel_and_accepts_only_final_json(self):
        calls, manifest = self.execute()
        self.assertEqual(["format" in row for row in calls], [True, False, False, True])
        self.assertEqual(calls[0], calls[3])
        self.assertEqual(calls[1], calls[2])
        self.assertEqual([r["accepted"] for r in manifest["observations"]], [False, True, True, False])
        self.assertTrue(manifest["evidence_verified"])
        self.assertEqual(manifest["verified_acceptance"], [False, True, True, False])
        self.assertEqual((manifest["api_calls"], manifest["api_responses"]), (4, 4))
        self.assertFalse(manifest["native_execution"])

    def test_transport_failure_stops_without_retry(self):
        calls, manifest = self.execute("timeout")
        self.assertEqual(len(calls), 1)
        self.assertEqual(manifest["status"], "stopped")
        self.assertEqual((manifest["api_calls"], manifest["api_responses"]), (1, 0))

    def test_identity_drift_withdraws_verified_acceptance_but_keeps_counts(self):
        _, manifest = self.execute("identity")
        self.assertFalse(manifest["evidence_verified"])
        self.assertIsNone(manifest["verified_acceptance"])
        self.assertEqual(manifest["api_calls"], 4)

    def test_missing_receipt_withdraws_acceptance_and_counts(self):
        _, manifest = self.execute("receipt")
        self.assertFalse(manifest["evidence_verified"])
        self.assertIsNone(manifest["verified_acceptance"])
        self.assertIsNone(manifest["api_calls"])


if __name__ == "__main__":
    unittest.main()
