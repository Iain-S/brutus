"""Profile isolation, feasibility gating and audit lifecycle without model calls."""

from contextlib import redirect_stdout
import copy
import hashlib
from io import BytesIO, StringIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / "examples"))
import compound_planner as protocol
import compound_planner_order as ordering
import probe_compound_capability as capability
import test_compound_order_probe as fixtures


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ProbeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.execute()
        self.reference = self.fixture.root / "probe"
        self.directory = self.fixture.root / "capability"
        pin = patch.object(capability, "REFERENCE_MANIFEST_SHA256",
                           hashlib.sha256((self.reference / "manifest.json").read_bytes()).hexdigest(), create=True)
        pin.start()
        self.addCleanup(pin.stop)
        manifest = json.loads((self.reference / "manifest.json").read_text())
        paths = {"manifest.json", "frozen-2.json", "frozen-3.json"}
        paths.update("source/" + name for name in manifest["source_sha256"])
        paths.update("historical/" + name for name in manifest["historical_sha256"])
        for index, condition in enumerate(manifest["schedule"]):
            paths.update(f"call-{index:02d}-d{condition['decision_id']}/{name}" for name in (
                "condition.json", "selection.request.json", "selection.response.body",
                "selection.response.json", "selection.audit.json", "selection.http.json"))
        hashes = {name: hashlib.sha256((self.reference / name).read_bytes()).hexdigest() for name in paths}
        inventory_pin = patch.object(capability, "REFERENCE_INVENTORY_SHA256", protocol.digest(hashes), create=True)
        inventory_pin.start()
        self.addCleanup(inventory_pin.stop)

    def test_profiles_only_change_model_think_and_generated_budget(self):
        frozen = capability.load_reference(self.reference)
        base = frozen[2]["base_request"]
        original = copy.deepcopy(base)
        for profile in ("instruct", "thinking"):
            body = capability.profile_request(base, ordering.IDS, profile)
            plain = ordering.ordered_request(base, ordering.IDS)
            expected = copy.deepcopy(plain)
            if profile == "thinking":
                expected["model"] = capability.THINK_MODEL
                expected["think"] = True
                expected["options"]["num_predict"] = 1536
            self.assertEqual(body, expected)
        self.assertEqual(base, original)
        with self.assertRaises(ValueError): capability.profile_request(base, ordering.IDS, "invented")

    def test_schedule_has_two_controls_then_canary_then_balanced_thinking(self):
        rows = capability.schedule()
        self.assertEqual(len(rows), 16)
        self.assertEqual([r["profile"] for r in rows[:2]], ["instruct", "instruct"])
        self.assertTrue(rows[2]["canary"])
        self.assertEqual(rows[2]["decision_id"], 3)
        self.assertEqual(rows[2]["order"], list(ordering.IDS))
        for state in (2, 3):
            conditions = [r for r in rows if r["profile"] == "thinking" and r["decision_id"] == state]
            self.assertEqual(len(conditions), 7)
            self.assertEqual(len({tuple(r["order"]) for r in conditions if not r["repeat_control"]}), 6)
            self.assertTrue(conditions[-1]["repeat_control"])

    def execute(self, mode="success"):
        calls = []
        checks = []
        def transport(request_path, raw_path, status_path, timeout):
            body = json.loads(Path(request_path).read_text())
            calls.append(body)
            state = json.loads(body["prompt"])["decision_id"]
            thinking = body["model"] == capability.THINK_MODEL
            choice = "wait" if thinking else "compound"
            if mode == "baseline_drift" and not thinking: choice = "single"
            answer = {"decision_id": state, "candidate_id": choice}
            result = {"model": body["model"], "done": True, "done_reason": "stop",
                      "prompt_eval_count": 5800, "eval_count": 30,
                      "response": json.dumps(answer)}
            if thinking:
                result["thinking"] = "fixture reasoning, unverified"
                if mode == "length": result.update(done_reason="length", eval_count=1536, response="")
                if mode == "failed_counts": result.update(done_reason="length", eval_count=1536, response="")
                if mode == "missing_thinking": result.pop("thinking")
                if mode == "wrong_channel": result.update(thinking=json.dumps(answer), response="", eval_count=19)
                if mode == "partial_timeout":
                    Path(raw_path).write_bytes(b'{"partial":')
                    protocol.write_json(status_path, {"http_status": 200, "body_complete": False})
                    raise TimeoutError("partial response deadline")
            Path(raw_path).write_bytes(json.dumps(result).encode())
            protocol.write_json(status_path, {"http_status": 200, "body_complete": True})
        def metadata():
            checks.append(True)
            result = {"server_version": "0.16.2"}
            for name, profile in capability.PROFILES.items():
                result[name] = {"model": profile["model"], "digest": profile["digest"],
                    "show": {"template": "fixture template", "parameters": "fixture defaults",
                             "model_info": {"general.parameter_count": 4000000000},
                             "capabilities": ["completion", "thinking"] if name == "thinking" else ["completion"]}}
            if mode == "missing_template": result["thinking"]["show"].pop("template")
            if len(checks) == 2:
                if mode == "metadata_changed": result["thinking"]["digest"] = "changed"
                if mode == "missing_audit":
                    (self.directory / "call-00-instruct-d2" / "selection.audit.json").unlink()
                if mode == "failed_counts":
                    path = self.directory / "call-02-thinking-d3" / "selection.audit.json"
                    audit = json.loads(path.read_text())
                    audit.update(api_calls=0, api_responses=0)
                    protocol.write_json(path, audit)
            return result
        with patch.object(protocol, "run_transport", side_effect=transport), \
             patch.object(capability, "model_metadata", side_effect=metadata), \
             patch("julius_gym.JuliusEnv.__init__", side_effect=AssertionError("No native environment allowed")), \
             redirect_stdout(StringIO()):
            if mode == "success":
                capability.run_probe(self.reference, self.directory)
            else:
                with self.assertRaises((ValueError, RuntimeError, TimeoutError)):
                    capability.run_probe(self.reference, self.directory)
        return calls, json.loads((self.directory / "manifest.json").read_text())

    def test_complete_profile_probe_has_sixteen_calls_and_no_native_execution(self):
        calls, manifest = self.execute()
        self.assertEqual(len(calls), 16)
        self.assertEqual(manifest["status"], "finished")
        self.assertEqual((manifest["api_calls"], manifest["api_responses"]), (16, 16))
        self.assertTrue(manifest["gates"]["instruct_reproduced"])
        self.assertTrue(manifest["gates"]["thinking_canary_feasible"])
        self.assertTrue(manifest["gates"]["thinking_sweep_complete"])
        self.assertFalse(manifest["native_execution"])
        self.assertEqual(manifest["executed_choices"], 0)
        self.assertEqual(calls[3], calls[-2])
        self.assertEqual(calls[2], calls[-1])

    def test_length_limited_canary_is_failure_without_retry_or_sweep(self):
        calls, manifest = self.execute("length")
        self.assertEqual(len(calls), 3)
        self.assertEqual(manifest["status"], "error")
        self.assertEqual(len(manifest["results"]), 2)
        self.assertFalse(manifest["gates"]["thinking_canary_feasible"])
        self.assertFalse(manifest["gates"]["thinking_sweep_complete"])
        raw = list(self.directory.glob("call-02-*/selection.response.body"))[0]
        self.assertEqual(json.loads(raw.read_bytes())["done_reason"], "length")

    def test_missing_thinking_is_not_promoted_to_reasoning_success(self):
        calls, manifest = self.execute("missing_thinking")
        self.assertEqual(len(calls), 3)
        self.assertFalse(manifest["gates"]["thinking_canary_feasible"])

    def test_instruct_drift_stops_before_reasoning_profile(self):
        calls, manifest = self.execute("baseline_drift")
        self.assertEqual(len(calls), 1)
        self.assertFalse(manifest["gates"]["instruct_reproduced"])
        self.assertEqual(manifest["gates"]["thinking_canary_feasible"], None)

    def test_reference_identity_is_pinned(self):
        path = self.reference / "manifest.json"
        value = json.loads(path.read_text())
        value["extra"] = "coherent substitute"
        protocol.write_json(path, value)
        with self.assertRaises(ValueError): capability.load_reference(self.reference)

    def test_reference_missing_receipts_or_coherent_telemetry_change_rejects(self):
        child = self.reference / "call-00-d2"
        for name in ("condition.json", "selection.http.json"):
            path = child / name
            content = path.read_bytes()
            path.unlink()
            with self.subTest(name=name), self.assertRaises(ValueError): capability.load_reference(self.reference)
            path.write_bytes(content)
        raw_path = child / "selection.response.body"
        raw = json.loads(raw_path.read_bytes())
        raw["eval_count"] += 1
        raw_path.write_bytes(json.dumps(raw).encode())
        protocol.write_json(child / "selection.response.json", raw)
        audit_path = child / "selection.audit.json"
        audit = json.loads(audit_path.read_text())
        audit["eval_count"] = raw["eval_count"]
        protocol.write_json(audit_path, audit)
        with self.assertRaises(ValueError): capability.load_reference(self.reference)

    def test_missing_accepted_audit_withdraws_verified_success_gates(self):
        _, manifest = self.execute("missing_audit")
        self.assertIsNone(manifest["api_calls"])
        self.assertIsNone(manifest["gates"]["thinking_canary_feasible"])
        self.assertFalse(manifest["gates"]["thinking_sweep_complete"])
        self.assertTrue(manifest["observations"]["thinking_canary_completed"])
        self.assertNotIn("repeat_controls_agree", manifest)

    def test_failed_audit_counts_cannot_contradict_complete_http_response(self):
        calls, manifest = self.execute("failed_counts")
        self.assertEqual(len(calls), 3)
        self.assertIsNone(manifest["api_calls"])
        self.assertTrue(manifest["audit_errors"])

    def test_partial_timeout_preserves_known_receipts_and_failed_gate(self):
        calls, manifest = self.execute("partial_timeout")
        self.assertEqual(len(calls), 3)
        self.assertEqual((manifest["api_calls"], manifest["api_responses"]), (3, 3))
        self.assertFalse(manifest["gates"]["thinking_canary_feasible"])
        self.assertFalse(manifest["audit_errors"])

    def test_changed_model_metadata_withholds_gates_without_erasing_counts(self):
        calls, manifest = self.execute("metadata_changed")
        self.assertEqual(len(calls), 16)
        self.assertEqual(manifest["api_calls"], 16)
        self.assertFalse(manifest["gates"]["profile_identity_verified"])
        self.assertIsNone(manifest["gates"]["thinking_canary_feasible"])
        self.assertEqual(manifest["models_after"]["thinking"]["digest"], "changed")

    def test_incomplete_model_template_evidence_stops_before_inference(self):
        calls, manifest = self.execute("missing_template")
        self.assertEqual(len(calls), 0)
        self.assertEqual(manifest["status"], "error")

    def test_model_metadata_retains_observed_wrong_digest_before_validation(self):
        tags = {"models": [{"name": capability.INSTRUCT_MODEL, "digest": capability.INSTRUCT_DIGEST},
                           {"name": capability.THINK_MODEL, "digest": "observed-wrong-digest"}]}
        def network(request, timeout):
            if isinstance(request, str):
                value = tags if request.endswith("/tags") else {"version": "0.16.2"}
            else:
                value = {"capabilities": ["completion", "thinking"], "template": "fixture", "parameters": "fixture"}
            return BytesIO(json.dumps(value).encode())
        with patch.object(capability.urllib.request, "urlopen", side_effect=network):
            metadata = capability.model_metadata()
        self.assertEqual(metadata["thinking"]["digest"], "observed-wrong-digest")

    def test_parameter_group_display_order_does_not_change_profile_identity(self):
        before = {"server_version": "0.16.2"}
        for name, profile in capability.PROFILES.items():
            before[name] = {"model": profile["model"], "digest": profile["digest"], "show": {
                "template": "same template", "system": None, "model_info": {"parameters": 4000000000},
                "parameters": 'top_p 0.8\nstop "a"\nstop "b"\nrepeat_penalty 1',
                "capabilities": ["completion", "thinking"], "modelfile": "PARAMETER top_p 0.8\nPARAMETER stop a"}}
        after = copy.deepcopy(before)
        for name in capability.PROFILES:
            after[name]["show"]["parameters"] = 'repeat_penalty 1\nstop "a"\nstop "b"\ntop_p 0.8'
            after[name]["show"]["modelfile"] = "PARAMETER stop a\nPARAMETER top_p 0.8"
        self.assertEqual(capability.metadata_signature(before), capability.metadata_signature(after))
        after["thinking"]["show"]["parameters"] = after["thinking"]["show"]["parameters"].replace("top_p 0.8", "top_p 0.9")
        self.assertNotEqual(capability.metadata_signature(before), capability.metadata_signature(after))
        after = copy.deepcopy(before)
        after["thinking"]["show"]["parameters"] = 'top_p 0.8\nstop "b"\nstop "a"\nrepeat_penalty 1'
        self.assertNotEqual(capability.metadata_signature(before), capability.metadata_signature(after))

    def test_answer_shaped_thinking_is_never_used_as_final_response(self):
        calls, manifest = self.execute("wrong_channel")
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(manifest["results"]), 2)
        self.assertFalse(manifest["gates"]["thinking_canary_feasible"])
        self.assertFalse(manifest["gates"]["thinking_sweep_complete"])
        self.assertEqual(manifest["api_calls"], 3)


if __name__ == "__main__":
    unittest.main()
