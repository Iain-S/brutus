"""Experimental compound request protocol and audited local inference."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

import ollama_planner as adapter

OPTIONS = dict(temperature=.7, top_p=.8, top_k=20, min_p=0., context_tokens=8192,
               forecast_format="overrides")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    encoded = json.dumps(value, indent=2, allow_nan=False)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(encoded, encoding="utf-8")
    temporary.replace(path)


def proposal_request(context, model, phase):
    if phase not in ("first", "successor"):
        raise ValueError("Unknown compound proposal phase")
    body = adapter.request_body(context, model, 256, **OPTIONS)
    compact = json.loads(body["prompt"])
    compact["compound_phase"] = phase
    compact["context_sha256"] = digest(context)
    if "compound_prefix" in context:
        compact["simulated_prefix"] = {key: copy.deepcopy(context["compound_prefix"][key])
                                       for key in ("candidate_id", "ticks", "forecast", "observation")}
    body["prompt"] = json.dumps(compact, allow_nan=False)
    body["format"]["properties"]["reason"]["maxLength"] = 2000
    body["system"] += (
        " This chooses the first macro of a two-step proposal; a successor menu will follow."
        if phase == "first" else
        " This menu is the native simulated successor after the reported first macro. "
        "Choose the second macro for that plan. It will be revalidated before any live execution.")
    return body


def validate_proposal(value, context):
    if (type(value) is not dict or set(value) != {"decision_id", "candidate_id", "reason"}
            or type(value["decision_id"]) is not int or value["decision_id"] != context["decision_id"]
            or type(value["candidate_id"]) is not str
            or value["candidate_id"] not in {c["id"] for c in context["candidates"]}
            or type(value["reason"]) is not str or len(value["reason"]) > 2000):
        raise ValueError("Proposal must select a current candidate with the exact schema")
    return value["candidate_id"]


def comparison(context, previews, proposal):
    if set(previews) != {"compound", "single"}:
        raise ValueError("Require compound and first-macro-only previews")
    ids = proposal["candidate_ids"]
    successor = proposal["successor"]
    prefix = successor["compound_prefix"]
    if (len(ids) != 2 or successor["decision_id"] != context["decision_id"]
            or prefix["candidate_id"] != ids[0] or type(prefix["ticks"]) is not int or prefix["ticks"] != 800
            or ids[0] not in {c["id"] for c in context["candidates"]}
            or ids[1] not in {c["id"] for c in successor["candidates"]}
            or previews["compound"]["candidate_ids"] != ids
            or previews["single"]["candidate_ids"] != [ids[0], "wait"]):
        raise ValueError("Preview names must match the model proposal and its successor menu")
    first_stages = []
    for name, preview in previews.items():
        stages = preview["plan"].get("stages", [])
        if len(stages) != 2 or stages[0]["candidate_id"] != ids[0]:
            raise ValueError("Preview requires both proposed stages")
        first = stages[0]
        facts = {"candidate_id": first["candidate_id"], "ticks": first["after"]["ticks"],
                 "forecast": first["after"], "observation": first["after_observation"],
                 "diagnostics": first["diagnostics"], "steps": first["steps"]}
        if (canonical(facts) != canonical(prefix) or len(first["steps"]) != 800
                or first["before_observation"] != context["state"]
                or stages[1]["before_observation"] != prefix["observation"]
                or stages[1]["candidate_id"] != (ids[1] if name == "compound" else "wait")):
            raise ValueError("Preview prefix differs from the native successor shown to the model")
        first_stages.append(first)
    if canonical(first_stages[0]) != canonical(first_stages[1]):
        raise ValueError("Compound and single previews do not share the same native first stage")
    branches = {name: preview["plan"] for name, preview in previews.items()}
    branches["wait"] = previews["compound"]["control"]
    for preview in previews.values():
        if preview["equal_time"] is not True or canonical(preview["control"]) != canonical(branches["wait"]):
            raise ValueError("Require identical equal-time wait controls")
    rows = []
    for name, branch in branches.items():
        if (branch["valid"] is not True or branch["status"] != "completed"
                or type(branch["ticks"]) is not int or branch["ticks"] != 1600
                or type(branch["forecast"]["ticks"]) is not int or branch["forecast"]["ticks"] != 1600
                or branch["forecast"]["status"] != "completed"):
            raise ValueError("Comparison requires completed valid equal 1600-tick endpoints")
        workers = {}
        for building in branch["diagnostics"]["buildings"]:
            key = str(building["type"])
            workers[key] = workers.get(key, 0) + building["workers"]
        rows.append({"id": name, "candidate_ids": previews[name]["candidate_ids"] if name != "wait" else ["wait", "wait"],
                     "ticks": branch["ticks"], "status": branch["status"],
                     "forecast": copy.deepcopy(branch["forecast"]),
                     "observation": copy.deepcopy(branch["observation"]),
                     "workers_by_building_type": workers})
    groups = {}
    for name, branch in branches.items():
        groups.setdefault(digest(branch["steps"]), []).append(name)
    return {"context_sha256": digest(context), "previews_sha256": digest(previews),
            "proposal_sha256": digest(proposal),
            "evidence_origin": "native_adapter", "model_reasoning_verified": False,
            "alternatives": rows, "equal_time_ticks": 1600,
            "equivalent_action_traces": [group for group in groups.values() if len(group) > 1]}


def selection_request(context, previews, proposal, model):
    body = adapter.request_body(context, model, 256, **OPTIONS)
    compact = json.loads(body["prompt"])
    for key in ("candidate_columns", "candidates", "forecast_columns", "forecast_baseline",
                "forecast_semantics", "forecast_policy"):
        compact.pop(key, None)
    compact["native_comparison"] = comparison(context, previews, proposal)
    body["prompt"] = json.dumps(compact, allow_nan=False)
    body["format"] = {"type": "object", "properties": {
        "decision_id": {"type": "integer", "enum": [context["decision_id"]]},
        "candidate_id": {"type": "string", "enum": ["compound", "single", "wait"]}},
        "required": ["decision_id", "candidate_id"], "additionalProperties": False}
    suffix = "Return required JSON only. Keep the reason under eight words."
    if not body["system"].endswith(suffix):
        raise ValueError("Unexpected adapter instruction")
    body["system"] = body["system"][:-len(suffix)] + (
        "Choose compound, single or wait using their equal-time native endpoints. "
        "compound executes both proposed macros; single executes your first macro then waits; "
        "wait builds nothing. Compare native goals, staffing, inventories, ratings and finances. "
        "Forecasts are simulated outcomes, not delivered results or guaranteed later progress. "
        "Return decision_id and candidate_id only; no reason or factual quotations.")
    return body


def validate_selection(value, context, previews, proposal):
    facts = comparison(context, previews, proposal)
    if (type(value) is not dict or set(value) != {"decision_id", "candidate_id"}
            or type(value["decision_id"]) is not int or value["decision_id"] != context["decision_id"]
            or type(value["candidate_id"]) is not str
            or value["candidate_id"] not in {row["id"] for row in facts["alternatives"]}):
        raise ValueError("Final selection must use the exact current alternative schema")
    return value["candidate_id"]


def _transport_worker(request_path, raw_path, status_path, url):
    body = Path(request_path).read_bytes()
    request = urllib.request.Request(url, body, {"Content-Type": "application/json"})
    try:
        response = urllib.request.urlopen(request, timeout=170)
    except urllib.error.HTTPError as failure:
        response = failure
    with response:
        status = {"http_status": response.status, "body_complete": False}
        write_json(status_path, status)
        size = 0
        with Path(raw_path).open("wb") as output:
            while True:
                chunk = response.read1(65536)
                if not chunk:
                    break
                output.write(chunk)
                output.flush()
                size += len(chunk)
                if size > 2 * 1024 * 1024:
                    raise ValueError("Inference response exceeds audit bound")
        write_json(status_path, {**status, "body_complete": True})


def run_transport(request_path, raw_path, status_path, timeout,
                  url="http://127.0.0.1:11434/api/generate"):
    """A separate process makes the wall-clock deadline independent of socket I/O."""
    command = [sys.executable, str(Path(__file__).resolve()), "--transport-worker",
               str(request_path), str(raw_path), str(status_path), url]
    try:
        result = subprocess.run(command, timeout=timeout, capture_output=True, check=False)
    except subprocess.TimeoutExpired as error:
        raise TimeoutError("Local inference exceeded its process deadline") from error
    if result.returncode:
        raise RuntimeError("Local inference transport failed: " + result.stderr.decode(errors="replace")[-1000:])


class AuditedModel:
    """One local inference attempt per call; durable acceptance precedes return."""

    def __init__(self, directory, model):
        self.directory, self.model = Path(directory), model

    def call(self, stage, body, validate):
        started = time.monotonic()
        audit = {"stage": stage, "status": "prepared", "api_calls": 0, "api_responses": 0,
                 "request_sha256": digest(body), "retries": 0}
        audit_path = self.directory / f"{stage}.audit.json"
        write_json(self.directory / f"{stage}.request.json", body)
        write_json(audit_path, audit)
        status_path = self.directory / f"{stage}.http.json"
        raw_path = self.directory / f"{stage}.response.body"
        def received_status():
            if status_path.exists():
                status = json.loads(status_path.read_text(encoding="utf-8"))
                audit.update(status)
                audit["api_responses"] = 1
        try:
            remaining = 170 - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("Inference deadline expired before transport")
            audit.update(api_calls=1, status="in_flight")
            write_json(audit_path, audit)
            run_transport(self.directory / f"{stage}.request.json", raw_path, status_path, remaining)
            received_status()
            raw = raw_path.read_bytes()
            if audit.get("http_status", 500) >= 400 or audit.get("body_complete") is not True:
                raise RuntimeError(f"Local inference HTTP status {audit.get('http_status')}, incomplete or failed response")
            if time.monotonic() - started >= 170:
                raise TimeoutError("Inference exceeded its acceptance deadline")
            if len(raw) > 2 * 1024 * 1024:
                raise ValueError("Inference response exceeds audit bound")
            result = json.loads(raw, object_pairs_hook=adapter.unique_response_object)
            if type(result) is not dict:
                raise ValueError("Inference API response must be an object")
            write_json(self.directory / f"{stage}.response.json", result)
            audit.update({key: result.get(key) for key in ("model", "done_reason", "prompt_eval_count",
                                                         "eval_count", "total_duration", "load_duration")})
            if result.get("model") != self.model:
                raise ValueError("Inference returned a different model")
            if (result.get("done") is not True or result.get("done_reason") != "stop"
                    or type(result.get("eval_count")) is not int
                    or not 1 <= result["eval_count"] <= body["options"]["num_predict"]):
                raise RuntimeError("Inference lacks strict successful completion telemetry")
            adapter.validate_inference_result(result, body["options"])
            if type(result.get("response")) is not str:
                raise ValueError("Inference response must contain JSON text")
            answer = json.loads(result["response"], object_pairs_hook=adapter.unique_response_object)
            validate(answer)
            if time.monotonic() - started >= 170:
                raise TimeoutError("Inference exceeded its acceptance deadline")
            audit.update(status="accepted", answer=answer, seconds=time.monotonic() - started)
            write_json(audit_path, audit)
            return answer
        except BaseException as error:
            received_status()
            audit.update(status="error", error=f"{type(error).__name__}: {error}",
                         seconds=time.monotonic() - started)
            write_json(audit_path, audit)
            raise


if __name__ == "__main__":
    if len(sys.argv) != 6 or sys.argv[1] != "--transport-worker":
        raise SystemExit("Use run_compound_planner.py for the experiment")
    _transport_worker(*sys.argv[2:])
