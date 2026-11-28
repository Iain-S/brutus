#!/usr/bin/env python3
"""Frozen final-selection order probe; never creates a native environment."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
from uuid import uuid4

import compound_planner as protocol
import compound_planner_order as ordering
from run_compound_planner import MODEL, MODEL_DIGEST, verify_model

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ANCHORS = {
    "run.json": "53ed8dd2b878bb82126158283b98cc777aabe6c1ad2fa6da7ca75b11f4c4d18f",
    "decision-02/selection.request.json": "0fa4b9da535783e7ebb5778d60a5bdc51f7319230c557ba2005a0fe8fc4f5286",
    "decision-03/selection.request.json": "4ea0badaaed9c1295beb7e2cb26b9169ba4caf0c1c553d9aafb86d993fc84801",
    "decision-02/selection.response.body": "206b486a9f4c50585caccec14bfec70b3e5c4ad361c35d32e443e73e4b18d991",
    "decision-03/selection.response.body": "2a35b4a7be4702d98aa4671c4bbcec2b2b6682bb4277ee7ec51137bc4676ffdd",
    "decision-02/selection.audit.json": "92ed83fa6466251ea8a92ac98812b352cfde31c8c32d85dfc4ddc9a2beae8491",
    "decision-03/selection.audit.json": "0583839d70708daebda34dc165863977c7bbdb1d55ea7aaa80fbed6202bfb4b4",
}
HISTORICAL_FILES = ("first.context.json", "proposal.json", "previews.json", "comparison.json",
                    "selection.request.json", "selection.response.body", "selection.response.json",
                    "selection.audit.json", "decision.json")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=protocol.adapter.unique_response_object)


def load_frozen(source):
    source = Path(source).resolve()
    for relative, expected in SOURCE_ANCHORS.items():
        if hashlib.sha256((source / relative).read_bytes()).hexdigest() != expected:
            raise ValueError("Historical source identity/hash differs from the designated frozen run")
    manifest = read_json(source / "run.json")
    if (manifest["status"] != "finished" or manifest["artifact_errors"]
            or not manifest["git_commit"].startswith("03089798")
            or manifest["summary"]["ticks"] != 6400 or manifest["summary"]["api_calls"] != 12
            or manifest["model_digest_before"] != MODEL_DIGEST or manifest["model_digest_after"] != MODEL_DIGEST):
        raise ValueError("Require the verified source compound run and pinned model")
    for name, expected in manifest["source_sha256"].items():
        if Path(name).name != name or hashlib.sha256((source / "source" / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Archived source snapshot differs from its recorded hash")
    for module in (protocol, protocol.adapter):
        current = Path(module.__file__)
        if current.read_bytes() != (source / "source" / current.name).read_bytes():
            raise ValueError("Frozen request reconstruction requires the original protocol/adapter source")
    frozen = {}
    for state in (2, 3):
        folder = source / f"decision-{state:02d}"
        context = read_json(folder / "first.context.json")
        proposal, previews = read_json(folder / "proposal.json"), read_json(folder / "previews.json")
        body = protocol.selection_request(context, previews, proposal, MODEL)
        if (context["decision_id"] != state
                or protocol.canonical(body) != protocol.canonical(read_json(folder / "selection.request.json"))
                or protocol.canonical(protocol.comparison(context, previews, proposal)) !=
                    protocol.canonical(read_json(folder / "comparison.json"))):
            raise ValueError("Frozen native inputs differ from the originally requested comparison")
        raw = json.loads((folder / "selection.response.body").read_bytes(),
                         object_pairs_hook=protocol.adapter.unique_response_object)
        if protocol.canonical(raw) != protocol.canonical(read_json(folder / "selection.response.json")):
            raise ValueError("Source parsed response differs from its raw API body")
        audit = read_json(folder / "selection.audit.json")
        if (raw.get("model") != MODEL or raw.get("done") is not True or raw.get("done_reason") != "stop"
                or type(raw.get("eval_count")) is not int or not 1 <= raw["eval_count"] <= 256
                or audit.get("stage") != "selection" or audit.get("status") != "accepted"
                or type(audit.get("api_calls")) is not int or audit["api_calls"] != 1
                or type(audit.get("api_responses")) is not int or audit["api_responses"] != 1
                or audit.get("model") != MODEL or audit.get("http_status") != 200
                or audit.get("body_complete") is not True or audit.get("request_sha256") != protocol.digest(body)
                or any(protocol.canonical(audit.get(key)) != protocol.canonical(raw.get(key))
                       for key in ("prompt_eval_count", "eval_count", "done_reason"))
                or type(audit.get("seconds")) not in (int, float) or not 0 <= audit["seconds"] < 170):
            raise ValueError("Historical inference lacks matching strict accepted telemetry")
        protocol.adapter.validate_inference_result(raw, body["options"])
        answer = json.loads(raw["response"], object_pairs_hook=protocol.adapter.unique_response_object)
        selected = protocol.validate_selection(answer, context, previews, proposal)
        decision = read_json(folder / "decision.json")
        if (decision["status"] != "completed" or decision["execution_verified"] is not True
                or protocol.canonical(decision["selection"]) != protocol.canonical(answer)
                or protocol.canonical(audit["answer"]) != protocol.canonical(answer)
                or decision["selected"] != selected):
            raise ValueError("Source decision is not verified or differs from its raw answer")
        inputs = {"context": context, "proposal": proposal, "previews": previews}
        frozen[state] = {**inputs, "base_request": body, "input_sha256": protocol.digest(inputs),
                         "historical_unseeded_selection": selected}
    return frozen


def server_version():
    with urllib.request.urlopen("http://127.0.0.1:11434/api/version", timeout=10) as response:
        return json.load(response)["version"]


def run_probe(source, directory):
    source, directory = Path(source).resolve(), Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    manifest = {"profile": "frozen-compound-order-seeded-v1", "status": "running",
                "source_run": str(source), "native_execution": False, "executed_choices": 0,
                "proposal_api_calls": 0, "model": MODEL, "model_digest": MODEL_DIGEST,
                "seed": ordering.SEED, "retries": 0, "fallbacks": 0,
                "schedule": ordering.schedule(), "max_api_calls": 14, "results": [],
                "conditions_started": [], "source_anchors": dict(SOURCE_ANCHORS),
                "api_calls": 0, "api_responses": 0}
    protocol.write_json(directory / "manifest.json", manifest)
    try:
        frozen = load_frozen(source)
        for state, data in frozen.items():
            protocol.write_json(directory / f"frozen-{state}.json", data)
        historical = directory / "historical"
        historical.mkdir()
        originals = ["run.json"]
        originals += [f"source/{name}" for name in read_json(source / "run.json")["source_sha256"]]
        originals += [f"decision-{state:02d}/{name}" for state in (2, 3) for name in HISTORICAL_FILES]
        manifest["historical_sha256"] = {}
        for relative in originals:
            content = (source / relative).read_bytes()
            target = historical / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            manifest["historical_sha256"][relative] = hashlib.sha256(content).hexdigest()
        # Validate the self-contained copy before allowing any inference.
        load_frozen(historical)
        source_dir = directory / "source"
        source_dir.mkdir()
        manifest["source_sha256"] = {}
        for path in (Path(__file__), Path(ordering.__file__), Path(protocol.__file__),
                     Path(protocol.adapter.__file__), Path(__file__).with_name("run_compound_planner.py")):
            content = path.read_bytes()
            (source_dir / path.name).write_bytes(content)
            manifest["source_sha256"][path.name] = hashlib.sha256(content).hexdigest()
        manifest["source_run_manifest_sha256"] = hashlib.sha256((source / "run.json").read_bytes()).hexdigest()
        manifest["server_version"] = server_version()
        manifest["model_digest_before"] = verify_model()
        manifest["git_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
            check=True, capture_output=True, text=True, timeout=5).stdout.strip()
        protocol.write_json(directory / "manifest.json", manifest)
        for index, condition in enumerate(manifest["schedule"]):
            data = frozen[condition["decision_id"]]
            child = directory / f"call-{index:02d}-d{condition['decision_id']}"
            child.mkdir()
            body = ordering.ordered_request(data["base_request"], condition["order"])
            protocol.write_json(child / "condition.json", {**condition, "input_sha256": data["input_sha256"],
                                                          "base_request_sha256": protocol.digest(data["base_request"])})
            manifest["conditions_started"].append({"index": index, "directory": child.name,
                                                   "decision_id": condition["decision_id"],
                                                   "request_sha256": protocol.digest(body)})
            protocol.write_json(directory / "manifest.json", manifest)
            value = protocol.AuditedModel(child, MODEL).call("selection", body,
                lambda answer: protocol.validate_selection(answer, data["context"], data["previews"], data["proposal"]))
            selected = protocol.validate_selection(value, data["context"], data["previews"], data["proposal"])
            manifest["results"].append({**condition, "index": index, "selected": selected,
                "selected_position": condition["order"].index(selected) + 1,
                "request_sha256": protocol.digest(body), "input_sha256": data["input_sha256"]})
            protocol.write_json(directory / "manifest.json", manifest)
            print(json.dumps(manifest["results"][-1]), flush=True)
        manifest["model_digest_after"] = verify_model()
        controls = {}
        for state in (2, 3):
            rows = [row for row in manifest["results"] if row["decision_id"] == state]
            if rows[0]["request_sha256"] != rows[-1]["request_sha256"]:
                raise ValueError("Repeated control request differs from its first presentation")
            controls[str(state)] = rows[0]["selected"] == rows[-1]["selected"]
        manifest.update(status="finished", repeat_controls_agree=controls)
    except BaseException as error:
        manifest.update(status="error", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        calls = responses = 0
        errors = []
        accepted = {row["index"]: row for row in manifest["results"]}
        for attempt in manifest["conditions_started"]:
            path = directory / attempt["directory"] / "selection.audit.json"
            try:
                audit = read_json(path)
                if (type(audit.get("api_calls")) is not int or audit["api_calls"] not in (0, 1)
                        or type(audit.get("api_responses")) is not int or not 0 <= audit["api_responses"] <= audit["api_calls"]
                        or audit.get("request_sha256") != attempt["request_sha256"]):
                    raise ValueError("Contradictory call counts or request hash")
                if attempt["index"] in accepted:
                    expected = {"decision_id": attempt["decision_id"],
                                "candidate_id": accepted[attempt["index"]]["selected"]}
                    if (audit.get("status") != "accepted" or audit.get("stage") != "selection"
                            or audit["api_calls"] != 1 or audit["api_responses"] != 1
                            or protocol.canonical(audit.get("answer")) != protocol.canonical(expected)):
                        raise ValueError("Accepted condition lacks its matching complete inference audit")
                calls += audit["api_calls"]
                responses += audit["api_responses"]
            except Exception as error:
                errors.append(f"{path}: {error}")
        manifest.update(api_calls=None if errors else calls, api_responses=None if errors else responses,
                        audit_errors=errors, seconds=time.monotonic() - started)
        if errors:
            manifest["status"] = "error"
        protocol.write_json(directory / "manifest.json", manifest)
        print(f"Frozen probe artifacts: {directory}", flush=True)
    if errors:
        raise RuntimeError("Inference audit is unreadable; probe cannot be accepted")
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "runs" / "planner-input-probes")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    directory = (args.runs_dir.resolve() / now.strftime("%Y-%m-%d") /
                 (now.strftime("%Y%m%dT%H%M%S.%fZ") + "_compound-order_" + uuid4().hex[:8]))
    run_probe(args.source_run, directory)


if __name__ == "__main__":
    main()
