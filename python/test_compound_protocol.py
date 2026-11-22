"""Strict compound model protocol and durable local inference boundaries."""

import copy
from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / "examples"))
import compound_planner as protocol


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.context = {"decision_id": 7, "state": {"population_total": 12, "ratings_peace": 3},
                        "forecast_policy": {"minimum_ticks": 800},
                        "candidates": [{"id": "housing", "ticks": 2, "forecast": {"ticks": 800}},
                                       {"id": "wait", "ticks": 800, "forecast": {"ticks": 800}}]}
        def branch(population):
            return {"ticks": 1600, "status": "completed", "valid": True,
                    "forecast": {"ticks": 1600, "status": "completed", "population": population},
                    "observation": {"population_total": population, "ratings_peace": 3},
                    "diagnostics": {"buildings": [{"type": 55, "workers": 6, "food": 0}],
                                    "food_supply": {"schema_version": 1}}, "steps": []}
        control = branch(12)
        prefix = {"candidate_id": "housing", "ticks": 800, "forecast": {"ticks": 800, "status": "completed"},
                  "observation": {"population_total": 20, "ratings_peace": 3},
                  "diagnostics": {"buildings": []}, "steps": [{"action": [0, 0, 0]}] * 800}
        self.proposal = {"candidate_ids": ["housing", "future"], "successor": {
            "decision_id": 7, "compound_prefix": prefix, "candidates": [{"id": "future"}, {"id": "wait"}]}}
        def stages(second):
            first = {"candidate_id": "housing", "after": prefix["forecast"],
                     "after_observation": prefix["observation"], "before_observation": self.context["state"],
                     "diagnostics": prefix["diagnostics"], "steps": prefix["steps"]}
            return [copy.deepcopy(first), {"candidate_id": second, "before_observation": prefix["observation"]}]
        self.previews = {"compound": {"candidate_ids": ["housing", "future"], "plan": branch(40),
                                      "control": control, "equal_time": True},
                         "single": {"candidate_ids": ["housing", "wait"], "plan": branch(30),
                                    "control": copy.deepcopy(control), "equal_time": True}}
        self.previews["compound"]["plan"]["stages"] = stages("future")
        self.previews["single"]["plan"]["stages"] = stages("wait")

    def test_proposal_keeps_whole_menu_and_exact_schema(self):
        before = copy.deepcopy(self.context)
        for phase in ("first", "successor"):
            body = protocol.proposal_request(self.context, "test-model", phase)
            self.assertEqual(body["format"]["properties"]["candidate_id"]["enum"], ["housing", "wait"])
            compact = json.loads(body["prompt"])
            self.assertEqual([r[0] for r in compact["candidates"]], ["housing", "wait"])
            self.assertEqual(compact["compound_phase"], phase)
            self.assertFalse(body["think"])
            self.assertEqual(body["options"], {"num_ctx": 8192, "num_predict": 256,
                                               "temperature": .7, "top_p": .8, "top_k": 20, "min_p": 0.})
        self.assertEqual(self.context, before)
        good = {"decision_id": 7, "candidate_id": "housing", "reason": "native goals"}
        self.assertEqual(protocol.validate_proposal(good, self.context), "housing")
        for update in ({"decision_id": True}, {"candidate_id": "missing"}, {"reason": 4},
                       {"reason": "x" * 2001}, {"extra": "claim"}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                protocol.validate_proposal({**good, **update}, self.context)

    def test_comparison_retains_native_facts_and_all_ratings(self):
        before = copy.deepcopy(self.previews)
        comparison = protocol.comparison(self.context, self.previews, self.proposal)
        self.assertEqual([r["id"] for r in comparison["alternatives"]], ["compound", "single", "wait"])
        self.assertEqual([r["forecast"]["population"] for r in comparison["alternatives"]], [40, 30, 12])
        self.assertTrue(all(r["observation"]["ratings_peace"] == 3 for r in comparison["alternatives"]))
        self.assertEqual(comparison["alternatives"][0]["workers_by_building_type"], {"55": 6})
        self.assertEqual(self.previews, before)
        body = protocol.selection_request(self.context, self.previews, self.proposal, "test-model")
        self.assertEqual(set(body["format"]["properties"]), {"decision_id", "candidate_id"})
        self.assertEqual(json.loads(body["prompt"])["native_comparison"], comparison)
        for name in ("compound", "single", "wait"):
            self.assertEqual(protocol.validate_selection({"decision_id": 7, "candidate_id": name},
                                                        self.context, self.previews, self.proposal), name)
        for value in ({"decision_id": True, "candidate_id": "compound"},
                      {"decision_id": 7, "candidate_id": "missing"},
                      {"decision_id": 7, "candidate_id": "compound", "reason": "claims"}):
            with self.assertRaises(ValueError):
                protocol.validate_selection(value, self.context, self.previews, self.proposal)

    def test_comparison_refuses_partial_invalid_or_unequal_branches(self):
        for kind in ("invalid", "duration", "control", "status", "float_ticks"):
            previews = copy.deepcopy(self.previews)
            if kind == "invalid": previews["compound"]["plan"]["valid"] = False
            if kind == "duration": previews["single"]["plan"]["ticks"] = 800
            if kind == "control": previews["single"]["control"]["forecast"]["population"] = 99
            if kind == "status": previews["compound"]["plan"]["status"] = "truncated"
            if kind == "float_ticks": previews["compound"]["plan"]["ticks"] = 1600.
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                protocol.comparison(self.context, previews, self.proposal)

    def test_swapped_root_actions_and_successor_diagnostics_reject(self):
        for kind in ("ids", "trace", "diagnostics", "shown_successor", "second"):
            previews, proposal = copy.deepcopy(self.previews), copy.deepcopy(self.proposal)
            if kind == "ids": previews["single"]["candidate_ids"][0] = "wait"
            if kind == "trace": previews["compound"]["plan"]["stages"][0]["steps"][0] = {"action": [5, 1, 1]}
            if kind == "diagnostics": previews["single"]["plan"]["stages"][0]["diagnostics"] = {"buildings": [99]}
            if kind == "shown_successor": proposal["successor"]["compound_prefix"]["observation"]["ratings_peace"] = 4
            if kind == "second": proposal["candidate_ids"][1] = "wait"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                protocol.comparison(self.context, previews, proposal)


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.body = {"model": "test-model", "options": {"num_ctx": 8192, "num_predict": 256}}
        self.answer = {"id": "chosen"}
        self.raw = json.dumps({"model": "test-model", "done": True, "done_reason": "stop",
                               "prompt_eval_count": 1000, "eval_count": 12,
                               "response": json.dumps(self.answer)}).encode()

    def call(self, raw=None, error=None, advance=0, audit_error=False):
        clock = {"now": 0}
        def network(request_path, raw_path, status_path, timeout):
            self.assertLessEqual(timeout, 170)
            inflight = json.loads((self.root / "first.audit.json").read_text())
            self.assertEqual(inflight["api_calls"], 1)
            self.assertEqual(inflight["status"], "in_flight")
            clock["now"] += advance
            if error: raise error
            Path(raw_path).write_bytes(self.raw if raw is None else raw)
            protocol.write_json(status_path, {"http_status": 200, "body_complete": True})
        original = protocol.write_json
        def write(path, value):
            if audit_error and value.get("status") == "accepted":
                raise OSError("audit disk failure")
            return original(path, value)
        with patch.object(protocol, "run_transport", side_effect=network), \
             patch.object(protocol.time, "monotonic", side_effect=lambda: clock["now"]), \
             patch.object(protocol, "write_json", side_effect=write):
            return protocol.AuditedModel(self.root, "test-model").call("first", self.body, lambda value: value)

    def test_complete_audit_precedes_return(self):
        self.assertEqual(self.call(), self.answer)
        self.assertEqual((self.root / "first.response.body").read_bytes(), self.raw)
        manifest = json.loads((self.root / "first.audit.json").read_text())
        self.assertEqual(manifest["status"], "accepted")
        self.assertEqual((manifest["api_calls"], manifest["api_responses"]), (1, 1))
        self.assertEqual(manifest["answer"], self.answer)
        self.assertEqual(json.loads((self.root / "first.request.json").read_text()), self.body)

    def test_malformed_duplicate_and_oversized_context_fail_with_raw_body(self):
        for raw in (b'{"done":true,"done":true}', b'not-json',
                    self.raw.replace(b'1000', b'8192'),
                    self.raw.replace(b'"stop"', b'"length"'),
                    self.raw.replace(b'"test-model"', b'"wrong-model"')):
            with self.subTest(raw=raw), self.assertRaises((ValueError, RuntimeError)):
                self.call(raw=raw)
            self.assertEqual((self.root / "first.response.body").read_bytes(), raw)
            self.assertEqual(json.loads((self.root / "first.audit.json").read_text())["status"], "error")

    def test_timeout_and_late_response_never_return_a_choice(self):
        with self.assertRaises(TimeoutError): self.call(error=TimeoutError("timeout"))
        self.assertEqual(json.loads((self.root / "first.audit.json").read_text())["api_responses"], 0)
        with self.assertRaises(TimeoutError): self.call(advance=171)
        self.assertEqual((self.root / "first.response.body").read_bytes(), self.raw)

    def test_audit_failure_never_returns_accepted_answer(self):
        with self.assertRaisesRegex(OSError, "audit disk failure"):
            self.call(audit_error=True)

    def test_incomplete_or_invalid_completion_telemetry_rejects(self):
        for update in ({"done": "false"}, {"done": 1}, {"done_reason": None},
                       {"eval_count": None}, {"eval_count": 0}, {"eval_count": 257}):
            raw = json.loads(self.raw)
            raw.update(update)
            with self.subTest(update=update), self.assertRaises(RuntimeError):
                self.call(raw=json.dumps(raw).encode())

    def test_http_failure_retains_body_and_counts_received_status(self):
        def network(request_path, raw_path, status_path, timeout):
            Path(raw_path).write_bytes(b'{"error":"local server failure"}')
            protocol.write_json(status_path, {"http_status": 500, "body_complete": True})
        with patch.object(protocol, "run_transport", side_effect=network):
            with self.assertRaisesRegex(RuntimeError, "500"):
                protocol.AuditedModel(self.root, "test-model").call("first", self.body, lambda value: value)
        audit = json.loads((self.root / "first.audit.json").read_text())
        self.assertEqual(audit["api_responses"], 1)
        self.assertEqual(audit["http_status"], 500)
        self.assertEqual((self.root / "first.response.body").read_bytes(), b'{"error":"local server failure"}')

    def test_real_transport_deadline_kills_slow_body_and_preserves_http_error(self):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        import threading
        import time
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_POST(self):
                self.send_response(500 if self.path == "/error" else 200)
                self.end_headers()
                if self.path == "/slow": time.sleep(5)
                try:
                    self.wfile.write(b'{"error":"fixture"}')
                except (BrokenPipeError, ConnectionResetError): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        request_path = self.root / "worker.request.json"
        protocol.write_json(request_path, self.body)
        raw_path, status_path = self.root / "raw.body", self.root / "status.json"
        base = f"http://127.0.0.1:{server.server_port}"
        protocol.run_transport(request_path, raw_path, status_path, 10, base + "/error")
        self.assertEqual(raw_path.read_bytes(), b'{"error":"fixture"}')
        self.assertEqual(json.loads(status_path.read_text())["http_status"], 500)
        started = time.monotonic()
        with self.assertRaises(TimeoutError):
            protocol.run_transport(request_path, raw_path, status_path, 1.5, base + "/slow")
        self.assertLess(time.monotonic() - started, 4)


if __name__ == "__main__":
    unittest.main()
