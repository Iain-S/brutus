#!/usr/bin/env python3
"""Bounded frozen thinking-profile feasibility and selection check; no game actions."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request
from uuid import uuid4

import compound_planner as protocol
import compound_planner_order as ordering
import probe_compound_order as baseline

ROOT = Path(__file__).resolve().parents[2]
REFERENCE_MANIFEST_SHA256 = "2490f47392d19a36305b0cf83861ede35720ef1bca9bf29367e955d2eb1c06ed"
REFERENCE_INVENTORY_SHA256 = "7bf8f8269e4b97c647d6a76288977106b22cbf832767db42205431430c1d2d12"
INSTRUCT_MODEL, INSTRUCT_DIGEST = baseline.MODEL, baseline.MODEL_DIGEST
THINK_MODEL = "qwen3:4b-thinking"
THINK_DIGEST = "359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7"
PROFILES = {"instruct": {"model": INSTRUCT_MODEL, "digest": INSTRUCT_DIGEST, "think": False, "tokens": 256},
            "thinking": {"model": THINK_MODEL, "digest": THINK_DIGEST, "think": True, "tokens": 1536}}


def profile_request(base, ids, profile):
    if profile not in PROFILES:
        raise ValueError("Unknown capability profile")
    body = ordering.ordered_request(base, ids)
    config = PROFILES[profile]
    body.update(model=config["model"], think=config["think"])
    body["options"]["num_predict"] = config["tokens"]
    return body


def schedule():
    rows = [{"profile": "instruct", "decision_id": state, "order": list(ordering.IDS),
             "canary": False, "repeat_control": False} for state in (2, 3)]
    orders = [row["order"] for row in ordering.schedule()[:12:2]]
    for index, ids in enumerate(orders):
        for state in ((3, 2) if index % 2 == 0 else (2, 3)):
            rows.append({"profile": "thinking", "decision_id": state, "order": list(ids),
                         "canary": index == 0 and state == 3, "repeat_control": False})
    rows.extend({"profile": "thinking", "decision_id": state, "order": list(ordering.IDS),
                 "canary": False, "repeat_control": True} for state in (2, 3))
    return rows


def inspect_call(child, body, data, thinking=False):
    audit = baseline.read_json(child / "selection.audit.json")
    http = baseline.read_json(child / "selection.http.json")
    raw = json.loads((child / "selection.response.body").read_bytes(),
                     object_pairs_hook=protocol.adapter.unique_response_object)
    if (protocol.canonical(raw) != protocol.canonical(baseline.read_json(child / "selection.response.json"))
            or raw.get("model") != body["model"] or raw.get("done") is not True or raw.get("done_reason") != "stop"
            or type(raw.get("eval_count")) is not int or not 1 <= raw["eval_count"] <= body["options"]["num_predict"]
            or audit.get("status") != "accepted" or audit.get("stage") != "selection"
            or type(audit.get("api_calls")) is not int or audit["api_calls"] != 1
            or type(audit.get("api_responses")) is not int or audit["api_responses"] != 1
            or audit.get("request_sha256") != protocol.digest(body)
            or audit.get("http_status") != 200 or audit.get("body_complete") is not True
            or protocol.canonical(http) != protocol.canonical({"http_status": 200, "body_complete": True})
            or type(audit.get("seconds")) not in (int, float)
            or not 0 <= audit["seconds"] < 170):
        raise ValueError("Call lacks matching strict accepted inference evidence")
    protocol.adapter.validate_inference_result(raw, body["options"])
    answer = json.loads(raw["response"], object_pairs_hook=protocol.adapter.unique_response_object)
    choice = protocol.validate_selection(answer, data["context"], data["previews"], data["proposal"])
    if protocol.canonical(audit["answer"]) != protocol.canonical(answer):
        raise ValueError("Raw answer differs from accepted audit")
    for key in ("model", "prompt_eval_count", "eval_count", "done_reason"):
        if protocol.canonical(audit.get(key)) != protocol.canonical(raw.get(key)):
            raise ValueError("Accepted telemetry differs from the raw response")
    trace = raw.get("thinking", "")
    if thinking and (type(trace) is not str or not trace.strip()):
        raise ValueError("Thinking profile lacks nonempty separate thinking output")
    return {"selected": choice, "thinking_characters": len(trace) if type(trace) is str else None,
            "generated_tokens": raw["eval_count"], "prompt_tokens": raw["prompt_eval_count"],
            "seconds": audit["seconds"]}


def reference_inventory(reference):
    manifest = baseline.read_json(reference / "manifest.json")
    names = {"manifest.json", "frozen-2.json", "frozen-3.json"}
    names.update("source/" + name for name in manifest["source_sha256"])
    names.update("historical/" + name for name in manifest["historical_sha256"])
    for index, condition in enumerate(manifest["schedule"]):
        names.update(f"call-{index:02d}-d{condition['decision_id']}/{name}" for name in (
            "condition.json", "selection.request.json", "selection.response.body",
            "selection.response.json", "selection.audit.json", "selection.http.json"))
    return {name: hashlib.sha256((reference / name).read_bytes()).hexdigest() for name in names}


def load_reference(reference):
    reference = Path(reference).resolve()
    if hashlib.sha256((reference / "manifest.json").read_bytes()).hexdigest() != REFERENCE_MANIFEST_SHA256:
        raise ValueError("Reference is not the pinned completed order diagnostic")
    try:
        if protocol.digest(reference_inventory(reference)) != REFERENCE_INVENTORY_SHA256:
            raise ValueError("Reference evidence inventory differs from its pinned bytes")
    except OSError as error:
        raise ValueError("Reference is missing required evidence") from error
    manifest = baseline.read_json(reference / "manifest.json")
    if (manifest["status"] != "finished" or manifest["api_calls"] != 14 or manifest["api_responses"] != 14
            or manifest["native_execution"] is not False or manifest["executed_choices"] != 0
            or manifest["schedule"] != ordering.schedule()
            or manifest["model_digest_before"] != INSTRUCT_DIGEST or manifest["model_digest_after"] != INSTRUCT_DIGEST
            or not all(manifest["repeat_controls_agree"].values())):
        raise ValueError("Reference inference, source or repeated-control gates failed")
    for name, expected in manifest["source_sha256"].items():
        content = (reference / "source" / name).read_bytes()
        if hashlib.sha256(content).hexdigest() != expected or content != Path(__file__).with_name(name).read_bytes():
            raise ValueError("Reference source snapshot differs from its executed protocol")
    for name, expected in manifest["historical_sha256"].items():
        if hashlib.sha256((reference / "historical" / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Reference historical record changed")
    frozen = baseline.load_frozen(reference / "historical")
    for state, data in frozen.items():
        if protocol.canonical(data) != protocol.canonical(baseline.read_json(reference / f"frozen-{state}.json")):
            raise ValueError("Frozen reference differs from original native facts")
    if len(manifest["results"]) != 14:
        raise ValueError("Reference is missing accepted conditions")
    for index, (condition, result) in enumerate(zip(ordering.schedule(), manifest["results"])):
        state = condition["decision_id"]
        body = profile_request(frozen[state]["base_request"], condition["order"], "instruct")
        child = reference / f"call-{index:02d}-d{state}"
        expected_condition = {**condition, "input_sha256": frozen[state]["input_sha256"],
                              "base_request_sha256": protocol.digest(frozen[state]["base_request"])}
        if protocol.canonical(baseline.read_json(child / "condition.json")) != protocol.canonical(expected_condition):
            raise ValueError("Reference condition proof differs from its native inputs")
        if protocol.canonical(body) != protocol.canonical(baseline.read_json(child / "selection.request.json")):
            raise ValueError("Reference request differs from declared frozen presentation")
        facts = inspect_call(child, body, frozen[state])
        if (result["index"] != index or any(result[key] != value for key, value in condition.items())
                or result["selected"] != facts["selected"] or result["request_sha256"] != protocol.digest(body)):
            raise ValueError("Reference accepted answer differs from its recorded condition")
    return frozen


def model_metadata():
    metadata = {}
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=10) as response:
            tags = json.load(response)["models"]
        metadata["tags"] = tags
    except Exception as error:
        return {"collection_error": f"tags: {error}"}
    for name, profile in PROFILES.items():
        observed = next((row for row in tags if row["name"] == profile["model"]), {})
        metadata[name] = {"model": profile["model"], "digest": observed.get("digest")}
        request = urllib.request.Request("http://127.0.0.1:11434/api/show",
            json.dumps({"model": profile["model"], "verbose": False}).encode(), {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                metadata[name]["show"] = json.load(response)
        except Exception as error:
            metadata[name]["collection_error"] = str(error)
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/version", timeout=10) as response:
            metadata["server_version"] = json.load(response)["version"]
    except Exception as error:
        metadata["version_error"] = str(error)
    return metadata


def validate_metadata(metadata):
    if type(metadata.get("server_version")) is not str or not metadata["server_version"]:
        raise ValueError("Missing observed server version")
    for name, expected in PROFILES.items():
        observed = metadata.get(name, {})
        show = observed.get("show", {})
        capabilities = show.get("capabilities", [])
        if (observed.get("model") != expected["model"] or observed.get("digest") != expected["digest"]
                or type(show.get("template")) is not str or not show["template"].strip()
                or type(show.get("parameters")) is not str or not show["parameters"].strip()
                or type(show.get("model_info")) is not dict or not show["model_info"]
                or type(capabilities) is not list or any(type(value) is not str for value in capabilities)
                or "completion" not in capabilities or (name == "thinking" and "thinking" not in capabilities)):
            raise ValueError("Required observed digest, template/defaults or capabilities are missing or changed")
        parameter_groups(show["parameters"])


def parameter_groups(parameters):
    """Ollama displays a parameter map; retain each key's ordered value list."""
    result = {}
    for line in parameters.splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            raise ValueError("Malformed displayed model parameter")
        result.setdefault(parts[0], []).append(parts[1].strip())
    return result


def metadata_signature(metadata):
    signature = {"server_version": metadata["server_version"]}
    for name in PROFILES:
        observed, show = metadata[name], metadata[name]["show"]
        # The generated modelfile repeats these fields and can reorder PARAMETER
        # lines. Preserve its raw text in the archive, not in effective identity.
        signature[name] = {"model": observed["model"], "digest": observed["digest"],
            "template": show["template"], "system": show.get("system"),
            "parameters": parameter_groups(show["parameters"]),
            "capabilities": sorted(show["capabilities"]), "model_info": show["model_info"],
            "details": show.get("details")}
    return signature


def transport_counts(child, attempt):
    """Verify even rejected attempts against independently written HTTP evidence."""
    body = baseline.read_json(child / "selection.request.json")
    audit = baseline.read_json(child / "selection.audit.json")
    if (protocol.digest(body) != attempt["request_sha256"]
            or audit.get("request_sha256") != attempt["request_sha256"]
            or audit.get("stage") != "selection" or audit.get("status") not in ("accepted", "error")
            or type(audit.get("api_calls")) is not int or audit["api_calls"] not in (0, 1)
            or type(audit.get("api_responses")) is not int or not 0 <= audit["api_responses"] <= audit["api_calls"]):
        raise ValueError("Incomplete or contradictory terminal inference audit")
    http_path, raw_path = child / "selection.http.json", child / "selection.response.body"
    if http_path.exists():
        http = baseline.read_json(http_path)
        if (audit["api_calls"] != 1 or audit["api_responses"] != 1
                or type(http.get("http_status")) is not int or type(http.get("body_complete")) is not bool
                or protocol.canonical({key: audit.get(key) for key in ("http_status", "body_complete")}) != protocol.canonical(http)
                or (http["body_complete"] and not raw_path.exists())):
            raise ValueError("Inference counters contradict the saved HTTP response")
    elif audit["api_responses"] != 0 or raw_path.exists() or (child / "selection.response.json").exists():
        raise ValueError("Missing HTTP receipt for a reported/raw response")
    if audit["status"] == "accepted" and (audit["api_calls"] != 1 or audit["api_responses"] != 1):
        raise ValueError("Accepted call must have one matching attempt and response")
    return audit["api_calls"], audit["api_responses"]


def run_probe(reference, directory):
    reference, directory = Path(reference).resolve(), Path(directory).resolve()
    if directory == reference or reference in directory.parents:
        raise ValueError("Capability output must be outside the reference directory")
    directory.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    manifest = {"profile": "thinking-selection-1536-v1", "status": "running", "reference": str(reference),
                "reference_manifest_sha256": REFERENCE_MANIFEST_SHA256, "profiles": PROFILES,
                "reference_inventory_sha256": REFERENCE_INVENTORY_SHA256,
                "schedule": schedule(), "max_api_calls": 16, "native_execution": False, "executed_choices": 0,
                "proposal_api_calls": 0, "retries": 0, "fallbacks": 0, "conditions_started": [], "results": [],
                "gates": {"instruct_reproduced": False, "thinking_canary_feasible": None,
                          "thinking_sweep_complete": False, "profile_identity_verified": None,
                          "reference_valid": False, "campaign_progress": "not_assessed"},
                "observations": {"instruct_reproduced": False, "thinking_canary_completed": None,
                                 "thinking_sweep_completed": False},
                "api_calls": 0, "api_responses": 0, "model_reasoning_verified": False}
    protocol.write_json(directory / "manifest.json", manifest)
    primary = None
    try:
        load_reference(reference)
        shutil.copytree(reference, directory / "reference")
        manifest["reference_copied"] = True
        frozen = load_reference(directory / "reference")
        manifest["gates"]["reference_valid"] = True
        source_dir = directory / "source"
        source_dir.mkdir()
        manifest["source_sha256"] = {}
        for path in (Path(__file__), Path(baseline.__file__), Path(ordering.__file__),
                     Path(protocol.__file__), Path(protocol.adapter.__file__)):
            content = path.read_bytes()
            (source_dir / path.name).write_bytes(content)
            manifest["source_sha256"][path.name] = hashlib.sha256(content).hexdigest()
        manifest["git_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
            capture_output=True, text=True, timeout=5).stdout.strip()
        manifest["models_before"] = model_metadata()
        protocol.write_json(directory / "manifest.json", manifest)
        validate_metadata(manifest["models_before"])
        expected_baseline = {r["decision_id"]: r["selected"] for r in
                             baseline.read_json(directory / "reference" / "manifest.json")["results"][:2]}
        for index, condition in enumerate(manifest["schedule"]):
            state, profile = condition["decision_id"], condition["profile"]
            data = frozen[state]
            body = profile_request(data["base_request"], condition["order"], profile)
            child = directory / f"call-{index:02d}-{profile}-d{state}"
            child.mkdir()
            if condition["canary"]:
                manifest["observations"]["thinking_canary_completed"] = False
            attempt = {**condition, "index": index, "directory": child.name,
                       "request_sha256": protocol.digest(body), "input_sha256": data["input_sha256"]}
            manifest["conditions_started"].append(attempt)
            protocol.write_json(child / "condition.json", attempt)
            protocol.write_json(directory / "manifest.json", manifest)
            def validate(answer):
                protocol.validate_selection(answer, data["context"], data["previews"], data["proposal"])
                if profile == "thinking":
                    raw = baseline.read_json(child / "selection.response.json")
                    if type(raw.get("thinking")) is not str or not raw["thinking"].strip():
                        raise ValueError("Thinking profile lacks nonempty separate thinking output")
            protocol.AuditedModel(child, PROFILES[profile]["model"]).call("selection", body, validate)
            facts = inspect_call(child, body, data, thinking=profile == "thinking")
            result = {**attempt, **facts, "selected_position": condition["order"].index(facts["selected"]) + 1}
            manifest["results"].append(result)
            if profile == "instruct" and facts["selected"] != expected_baseline[state]:
                raise ValueError("Instruct control drifted from its exact seeded historical request")
            if index == 1:
                manifest["observations"]["instruct_reproduced"] = True
            if condition["canary"]:
                manifest["observations"]["thinking_canary_completed"] = True
            protocol.write_json(directory / "manifest.json", manifest)
            print(json.dumps({k: result[k] for k in ("index", "profile", "decision_id", "selected", "generated_tokens")}), flush=True)
        controls = {}
        for state in (2, 3):
            rows = [r for r in manifest["results"] if r["profile"] == "thinking" and r["decision_id"] == state]
            if rows[0]["request_sha256"] != rows[-1]["request_sha256"]:
                raise ValueError("Thinking repeated-control requests differ")
            controls[str(state)] = rows[0]["selected"] == rows[-1]["selected"]
        manifest["observations"]["repeat_controls_agree"] = controls
        manifest["observations"]["thinking_sweep_completed"] = True
    except BaseException as error:
        primary = error
        manifest.update(status="error", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        audit_errors, metadata_errors, reference_errors = [], [], []
        calls, responses = 0, 0
        if manifest.get("reference_copied"):
            try:
                load_reference(directory / "reference")
            except Exception as error:
                reference_errors.append(str(error))
                manifest["gates"]["reference_valid"] = False
        if "models_before" in manifest:
            try:
                manifest["models_after"] = model_metadata()
                validate_metadata(manifest["models_before"])
                validate_metadata(manifest["models_after"])
                if protocol.canonical(metadata_signature(manifest["models_before"])) != protocol.canonical(metadata_signature(manifest["models_after"])):
                    raise ValueError("Installed model metadata changed during capability check")
                manifest["gates"]["profile_identity_verified"] = True
            except Exception as error:
                metadata_errors.append(str(error))
                manifest["gates"]["profile_identity_verified"] = False
        accepted = {r["index"]: r for r in manifest["results"]}
        for attempt in manifest["conditions_started"]:
            try:
                child = directory / attempt["directory"]
                call_count, response_count = transport_counts(child, attempt)
                if attempt["index"] in accepted:
                    body = baseline.read_json(child / "selection.request.json")
                    inspected = inspect_call(child, body, frozen[attempt["decision_id"]], attempt["profile"] == "thinking")
                    if inspected["selected"] != accepted[attempt["index"]]["selected"]:
                        raise ValueError("Accepted result differs from inference audit")
                calls += call_count
                responses += response_count
            except Exception as error:
                audit_errors.append(f"{attempt['directory']}: {error}")
        errors = audit_errors + metadata_errors + reference_errors
        manifest.update(api_calls=None if audit_errors else calls, api_responses=None if audit_errors else responses,
                        audit_errors=audit_errors, metadata_errors=metadata_errors, reference_errors=reference_errors,
                        seconds=time.monotonic() - started)
        if not errors and manifest["gates"]["profile_identity_verified"]:
            observed = manifest["observations"]
            manifest["gates"].update(instruct_reproduced=observed["instruct_reproduced"],
                thinking_canary_feasible=observed["thinking_canary_completed"],
                thinking_sweep_complete=observed["thinking_sweep_completed"])
            if observed["thinking_sweep_completed"]:
                manifest["repeat_controls_agree"] = observed["repeat_controls_agree"]
        else:
            manifest["gates"].update(instruct_reproduced=None, thinking_canary_feasible=None,
                                     thinking_sweep_complete=False)
        manifest["status"] = "error" if primary is not None or errors else "finished"
        protocol.write_json(directory / "manifest.json", manifest)
        print(f"Capability check artifacts: {directory}", flush=True)
    if errors and primary is None:
        raise RuntimeError("Capability audit/finalization failed: " + "; ".join(errors))
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-probe", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "runs" / "planner-input-probes")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    directory = (args.runs_dir.resolve() / now.strftime("%Y-%m-%d") /
                 (now.strftime("%Y%m%dT%H%M%S.%fZ") + "_thinking-capability_" + uuid4().hex[:8]))
    run_probe(args.reference_probe, directory)


if __name__ == "__main__":
    main()
