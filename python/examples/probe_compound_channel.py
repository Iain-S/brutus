#!/usr/bin/env python3
"""Four frozen thinking requests varying only provider schema; no game actions."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
from uuid import uuid4

import compound_planner as protocol
import compound_planner_order as ordering
import probe_compound_capability as capability

ROOT = Path(__file__).resolve().parents[2]
SCHEDULE = (True, False, False, True)


def request(base, schema):
    body = capability.profile_request(base, ordering.IDS, "thinking")
    if not schema:
        body.pop("format")
    return body


def inspect_attempt(child, attempt, data):
    """Describe rejected output without using the thinking field as an answer."""
    counts = capability.transport_counts(child, attempt)
    audit = capability.baseline.read_json(child / "selection.audit.json")
    body = capability.baseline.read_json(child / "selection.request.json")
    expected = request(data["base_request"], attempt["schema"])
    if protocol.canonical(body) != protocol.canonical(expected):
        raise ValueError("Request differs from declared single-field intervention")
    result = {"index": attempt["index"], "schema": attempt["schema"],
              "accepted": audit["status"] == "accepted", "error": audit.get("error"),
              "seconds": audit["seconds"], "api_calls": counts[0], "api_responses": counts[1]}
    raw_path = child / "selection.response.json"
    if raw_path.exists():
        raw = json.loads((child / "selection.response.body").read_bytes(),
                         object_pairs_hook=protocol.adapter.unique_response_object)
        if protocol.canonical(raw) != protocol.canonical(capability.baseline.read_json(raw_path)):
            raise ValueError("Raw/parsed inference records disagree")
        result.update(done=raw.get("done"), done_reason=raw.get("done_reason"),
                      generated_tokens=raw.get("eval_count"), prompt_tokens=raw.get("prompt_eval_count"),
                      final_characters=len(raw["response"]) if type(raw.get("response")) is str else None,
                      thinking_characters=len(raw["thinking"]) if type(raw.get("thinking")) is str else None)
    if result["accepted"]:
        result.update(capability.inspect_call(child, body, data, thinking=True))
    return result


def run_probe(reference, directory):
    reference, directory = Path(reference).resolve(), Path(directory).resolve()
    if directory == reference or reference in directory.parents:
        raise ValueError("Output must be outside reference")
    directory.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    manifest = {"profile": "thinking-channel-format-abba-v1", "status": "running",
                "schedule": list(SCHEDULE), "max_api_calls": 4, "conditions_started": [], "observations": [],
                "native_execution": False, "executed_choices": 0, "proposal_api_calls": 0,
                "retries": 0, "fallbacks": 0, "evidence_verified": False, "verified_acceptance": None,
                "campaign_progress": "not_assessed", "model_reasoning_verified": False}
    protocol.write_json(directory / "manifest.json", manifest)
    try:
        capability.load_reference(reference)
        shutil.copytree(reference, directory / "reference")
        data = capability.load_reference(directory / "reference")[3]
        manifest["git_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
            check=True, capture_output=True, text=True, timeout=5).stdout.strip()
        source = directory / "source"
        source.mkdir()
        manifest["source_sha256"] = {}
        for path in (Path(__file__), Path(capability.__file__), Path(capability.baseline.__file__),
                     Path(ordering.__file__), Path(protocol.__file__), Path(protocol.adapter.__file__)):
            content = path.read_bytes()
            (source / path.name).write_bytes(content)
            manifest["source_sha256"][path.name] = hashlib.sha256(content).hexdigest()
        manifest["models_before"] = capability.model_metadata()
        protocol.write_json(directory / "manifest.json", manifest)
        capability.validate_metadata(manifest["models_before"])
        for index, schema in enumerate(SCHEDULE):
            body = request(data["base_request"], schema)
            child = directory / f"call-{index:02d}"
            child.mkdir()
            attempt = {"index": index, "schema": schema, "directory": child.name,
                       "request_sha256": protocol.digest(body), "input_sha256": data["input_sha256"]}
            manifest["conditions_started"].append(attempt)
            protocol.write_json(child / "condition.json", attempt)
            protocol.write_json(directory / "manifest.json", manifest)
            def validate(answer):
                protocol.validate_selection(answer, data["context"], data["previews"], data["proposal"])
                raw = capability.baseline.read_json(child / "selection.response.json")
                if type(raw.get("thinking")) is not str or not raw["thinking"].strip():
                    raise ValueError("Missing separate thinking output")
            try:
                protocol.AuditedModel(child, capability.THINK_MODEL).call("selection", body, validate)
            except Exception:
                # Rejected complete output is the measurement. Transport or
                # deadline failure stops remaining predeclared conditions.
                audit = capability.baseline.read_json(child / "selection.audit.json")
                if (audit.get("http_status") != 200 or audit.get("body_complete") is not True
                        or audit.get("seconds", 170) >= 170
                        or not (child / "selection.response.json").exists()):
                    raise
            observation = inspect_attempt(child, attempt, data)
            manifest["observations"].append(observation)
            protocol.write_json(directory / "manifest.json", manifest)
            print(json.dumps(observation), flush=True)
        manifest["status"] = "finished"
    except Exception as error:
        manifest.update(status="stopped", error=f"{type(error).__name__}: {error}")
    finally:
        evidence_errors, audit_errors = [], []
        calls = responses = 0
        try:
            data = capability.load_reference(directory / "reference")[3]
            manifest["models_after"] = capability.model_metadata()
            capability.validate_metadata(manifest["models_before"])
            capability.validate_metadata(manifest["models_after"])
            if capability.metadata_signature(manifest["models_before"]) != capability.metadata_signature(manifest["models_after"]):
                raise ValueError("Model identity/defaults changed")
            for name, expected in manifest["source_sha256"].items():
                if hashlib.sha256((directory / "source" / name).read_bytes()).hexdigest() != expected:
                    raise ValueError("Executed source snapshot changed")
        except Exception as error:
            evidence_errors.append(str(error))
        for attempt in manifest["conditions_started"]:
            try:
                child = directory / attempt["directory"]
                if capability.baseline.read_json(child / "condition.json") != attempt:
                    raise ValueError("Condition record changed")
                c, r = capability.transport_counts(child, attempt)
                calls += c
                responses += r
                observed = [row for row in manifest["observations"] if row["index"] == attempt["index"]]
                if observed and inspect_attempt(child, attempt, data) != observed[0]:
                    raise ValueError("Observation differs from retained evidence")
            except Exception as error:
                audit_errors.append(f"{attempt['directory']}: {error}")
        errors = evidence_errors + audit_errors
        manifest.update(evidence_errors=evidence_errors, audit_errors=audit_errors,
                        api_calls=None if audit_errors else calls, api_responses=None if audit_errors else responses,
                        evidence_verified=not errors, seconds=time.monotonic() - started)
        if not errors and manifest["status"] == "finished":
            manifest["verified_acceptance"] = [r["accepted"] for r in manifest["observations"]]
        if errors:
            manifest["status"] = "error"
        protocol.write_json(directory / "manifest.json", manifest)
        print(f"Channel diagnostic artifacts: {directory}", flush=True)
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-probe", type=Path, required=True)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    directory = ROOT / "runs" / "planner-input-probes" / now.strftime("%Y-%m-%d") / (
        now.strftime("%Y%m%dT%H%M%S.%fZ") + "_thinking-channel_" + uuid4().hex[:8])
    run_probe(args.reference_probe, directory)
    if capability.baseline.read_json(directory / "manifest.json")["status"] != "finished":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
