"""Frozen-source integrity and no-native-execution lifecycle contracts."""

import copy
from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / "examples"))
import compound_planner as protocol
import probe_compound_order as probe
import test_compound_protocol as fixtures


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source-run"
        self.source.mkdir()
        source_dir = self.source / "source"
        source_dir.mkdir()
        hashes = {}
        for module in (protocol, protocol.adapter):
            path = Path(module.__file__)
            content = path.read_bytes()
            (source_dir / path.name).write_bytes(content)
            hashes[path.name] = hashlib.sha256(content).hexdigest()
        protocol.write_json(self.source / "run.json", {
            "git_commit": "03089798-fixture", "status": "finished", "artifact_errors": [],
            "summary": {"ticks": 6400, "api_calls": 12}, "source_sha256": hashes,
            "model_digest_before": probe.MODEL_DIGEST, "model_digest_after": probe.MODEL_DIGEST})
        for state in (2, 3):
            fixture = fixtures.ProtocolTests()
            fixture.setUp()
            context, proposal, previews = fixture.context, fixture.proposal, fixture.previews
            context["decision_id"] = state
            proposal["successor"]["decision_id"] = state
            folder = self.source / f"decision-{state:02d}"
            folder.mkdir()
            body = protocol.selection_request(context, previews, proposal, probe.MODEL)
            answer = {"decision_id": state, "candidate_id": "compound"}
            for name, value in (("first.context.json", context), ("proposal.json", proposal),
                                ("previews.json", previews), ("selection.request.json", body),
                                ("comparison.json", protocol.comparison(context, previews, proposal)),
                                ("decision.json", {"status": "completed", "execution_verified": True,
                                                   "selected": "compound", "selection": answer})):
                protocol.write_json(folder / name, value)
            response = {"model": probe.MODEL, "done": True, "done_reason": "stop",
                        "prompt_eval_count": 1000, "eval_count": 16, "response": json.dumps(answer)}
            protocol.write_json(folder / "selection.response.json", response)
            (folder / "selection.response.body").write_bytes(json.dumps(response).encode())
            protocol.write_json(folder / "selection.audit.json", {
                "stage": "selection", "status": "accepted", "api_calls": 1, "api_responses": 1,
                "request_sha256": protocol.digest(body), "model": probe.MODEL, "http_status": 200,
                "body_complete": True, "prompt_eval_count": 1000, "eval_count": 16,
                "done_reason": "stop", "seconds": 1., "answer": answer})
        paths = ["run.json"] + [f"decision-{state:02d}/{name}" for state in (2, 3) for name in
                  ("selection.request.json", "selection.response.body", "selection.audit.json")]
        anchors = {name: hashlib.sha256((self.source / name).read_bytes()).hexdigest() for name in paths}
        pin = patch.object(probe, "SOURCE_ANCHORS", anchors, create=True)
        pin.start()
        self.addCleanup(pin.stop)

    def execute(self, bad=False, audit_failure=False):
        calls = []
        def transport(request_path, raw_path, status_path, timeout):
            body = json.loads(Path(request_path).read_text())
            calls.append(body)
            state = json.loads(body["prompt"])["decision_id"]
            value = {"decision_id": state, "candidate_id": "invented" if bad else
                     body["format"]["properties"]["candidate_id"]["enum"][0]}
            Path(raw_path).write_text(json.dumps({"model": probe.MODEL, "done": True,
                "done_reason": "stop", "prompt_eval_count": 1000, "eval_count": 20,
                "response": json.dumps(value)}))
            protocol.write_json(status_path, {"http_status": 200, "body_complete": True})
        original = protocol.write_json
        def write(path, value):
            if audit_failure and Path(path).name == "selection.audit.json" and value.get("status") == "accepted":
                raise OSError("audit fixture failure")
            return original(path, value)
        with patch.object(protocol, "run_transport", side_effect=transport), \
             patch.object(probe, "verify_model", return_value=probe.MODEL_DIGEST), \
             patch.object(probe, "server_version", return_value="0.16.2"), \
             patch.object(protocol, "write_json", side_effect=write), \
             patch("julius_gym.JuliusEnv.__init__", side_effect=AssertionError("No native environment allowed")), \
             redirect_stdout(StringIO()):
            if bad or audit_failure:
                with self.assertRaises((ValueError, OSError)):
                    probe.run_probe(self.source, self.root / "probe")
            else:
                probe.run_probe(self.source, self.root / "probe")
        return calls, json.loads((self.root / "probe" / "manifest.json").read_text())

    def test_fourteen_calls_preserve_source_and_have_repeatable_controls(self):
        calls, manifest = self.execute()
        self.assertEqual(len(calls), 14)
        self.assertEqual(manifest["status"], "finished")
        self.assertEqual((manifest["api_calls"], manifest["api_responses"]), (14, 14))
        self.assertFalse(manifest["native_execution"])
        self.assertEqual(manifest["executed_choices"], 0)
        self.assertTrue(all(manifest["repeat_controls_agree"].values()))
        self.assertEqual(calls[0], calls[-1])
        self.assertEqual(calls[1], calls[-2])
        self.assertFalse(list((self.root / "probe").rglob("*.sav")))
        self.assertEqual(len(manifest["results"]), 14)
        self.source.rename(self.root / "unavailable-original")
        archived = probe.load_frozen(self.root / "probe" / "historical")
        self.assertEqual(set(archived), {2, 3})

    def test_coherent_substitute_run_is_not_the_pinned_source(self):
        path = self.source / "run.json"
        value = json.loads(path.read_text())
        value["synthetic_substitute"] = True
        protocol.write_json(path, value)
        with self.assertRaises(ValueError): probe.load_frozen(self.source)

    def test_historical_model_completion_and_audit_mismatch_reject(self):
        path = self.source / "decision-02" / "selection.response.body"
        original = json.loads(path.read_bytes())
        for update in ({"model": "wrong-model"}, {"done": "false"}, {"eval_count": None}, {"eval_count": 257}):
            changed = {**original, **update}
            path.write_bytes(json.dumps(changed).encode())
            protocol.write_json(path.with_name("selection.response.json"), changed)
            with patch.dict(probe.SOURCE_ANCHORS, {
                "decision-02/selection.response.body": hashlib.sha256(path.read_bytes()).hexdigest()}):
                with self.subTest(update=update), self.assertRaises(ValueError):
                    probe.load_frozen(self.source)

    def test_changed_source_facts_or_response_domain_reject_before_any_api(self):
        frozen = probe.load_frozen(self.source)
        self.assertEqual(set(frozen), {2, 3})
        path = self.source / "decision-02" / "previews.json"
        value = json.loads(path.read_text())
        value["compound"]["plan"]["forecast"]["population"] = 999
        protocol.write_json(path, value)
        with self.assertRaises(ValueError): probe.load_frozen(self.source)

    def test_source_snapshot_tampering_rejects(self):
        path = self.source / "source" / "compound_planner.py"
        path.write_text("tampered")
        with self.assertRaises(ValueError): probe.load_frozen(self.source)

    def test_invalid_answer_stops_without_retry_or_native_actions(self):
        calls, manifest = self.execute(bad=True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(manifest["status"], "error")
        self.assertEqual(manifest["api_calls"], 1)
        self.assertEqual(manifest["results"], [])

    def test_failed_accepted_audit_never_promotes_a_condition(self):
        calls, manifest = self.execute(audit_failure=True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(manifest["status"], "error")
        self.assertEqual(manifest["results"], [])

    def test_damaged_missing_or_contradictory_final_audit_is_unknown_and_failed(self):
        for mode in ("damaged", "missing", "contradictory", "request_hash"):
            directory = self.root / ("probe-" + mode)
            model_checks = []
            def check_model():
                model_checks.append(True)
                if len(model_checks) == 2:
                    path = directory / "call-00-d2" / "selection.audit.json"
                    if mode == "damaged": path.write_text("{truncated")
                    elif mode == "missing": path.unlink()
                    else:
                        audit = json.loads(path.read_text())
                        if mode == "contradictory": audit["api_calls"] = 0
                        else: audit["request_sha256"] = "changed"
                        protocol.write_json(path, audit)
                return probe.MODEL_DIGEST
            def model_call(model, stage, body, validate):
                state = json.loads(body["prompt"])["decision_id"]
                value = {"decision_id": state, "candidate_id": "wait"}
                validate(value)
                protocol.write_json(model.directory / "selection.audit.json", {
                    "stage": "selection", "status": "accepted", "api_calls": 1, "api_responses": 1,
                    "request_sha256": protocol.digest(body), "answer": value})
                return value
            with patch.object(probe, "verify_model", side_effect=check_model), \
                 patch.object(probe, "server_version", return_value="0.16.2"), \
                 patch.object(protocol.AuditedModel, "call", model_call), redirect_stdout(StringIO()):
                with self.subTest(mode=mode), self.assertRaisesRegex(RuntimeError, "audit"):
                    probe.run_probe(self.source, directory)
            manifest = json.loads((directory / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "error")
            self.assertIsNone(manifest["api_calls"])


if __name__ == "__main__":
    unittest.main()
