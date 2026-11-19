#!/usr/bin/env python3
"""Bounded two-stage local model command with adapter-owned native evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request
from uuid import uuid4

import ollama_planner as adapter
import ollama_planner_lookup as lookup

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT_ROOT = ROOT / "runs" / "planner-command-calls"


def _write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def _git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                              capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def run_lookup(context, args):
    started = time.monotonic()
    deadline = started + args.total_timeout
    now = datetime.now(timezone.utc)
    directory = (args.audit_root.expanduser().resolve() / now.strftime("%Y-%m-%d") /
                 (now.strftime("%Y%m%dT%H%M%S.%fZ") + "_lookup_" + uuid4().hex[:8]))
    options = dict(context_tokens=args.context_tokens, forecast_format=args.forecast_format,
                   temperature=args.temperature, top_p=args.top_p, top_k=args.top_k, min_p=args.min_p)
    manifest = dict(schema_version=1, profile="lookup-selection-id-only", evidence_origin="adapter",
                    started_utc=now.isoformat(), status="running", model=args.model, options=options,
                    max_tokens=args.max_tokens, api_timeout=args.api_timeout, total_timeout=args.total_timeout,
                    requests_prepared=0, api_calls=0, api_responses=0, retries=0, stages=[],
                    native_execution=False, executed_choices=0)

    def save():
        _write_json(directory / "manifest.json", manifest)

    def check_deadline():
        if time.monotonic() >= deadline:
            raise TimeoutError("Lookup command exceeded its total acceptance deadline")

    def summary(complete):
        result = dict(profile=manifest["profile"], evidence_origin="adapter", audit_directory=str(directory),
                      audit_complete=complete, status=manifest["status"], api_calls=manifest["api_calls"],
                      api_responses=manifest["api_responses"], seconds=manifest.get("seconds"),
                      context_sha256=manifest.get("context_sha256"),
                      stages=[{k: s[k] for k in ("stage", "status", "prompt_eval_count", "eval_count") if k in s}
                              for s in manifest["stages"]])
        for key in ("error", "audit_error"):
            if key in manifest:
                result[key] = manifest[key][:220]
        return result

    def call(stage_name, body):
        stage = dict(stage=stage_name, status="running", inference_validation="not_run",
                     protocol_validation="not_run", transport_state="prepared")
        manifest["stages"].append(stage)
        _write_json(directory / f"{stage_name}.request.json", body)
        manifest["requests_prepared"] += 1
        save()
        request = urllib.request.Request("http://127.0.0.1:11434/api/generate", json.dumps(body).encode("utf-8"),
                                         {"Content-Type": "application/json"})
        check_deadline()
        timeout = min(170, args.api_timeout, deadline - time.monotonic())
        stage["timeout_seconds"] = timeout
        stage["api_started_elapsed_seconds"] = time.monotonic() - started
        stage_started = time.monotonic()
        api_deadline = stage_started + timeout

        def check_api_deadline():
            if time.monotonic() >= api_deadline:
                raise TimeoutError("Local inference exceeded its per-API acceptance deadline")

        try:
            # No fallible audit I/O between counting an attempt and invoking transport.
            manifest["api_calls"] += 1
            stage["transport_state"] = "attempted"
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
            manifest["api_responses"] += 1
            stage["transport_state"] = "returned"
            data = raw.encode("utf-8") if type(raw) is str else raw
            (directory / f"{stage_name}.response.body").write_bytes(data)
            check_api_deadline()
            check_deadline()
            result = json.loads(data, object_pairs_hook=adapter.unique_response_object)
            _write_json(directory / f"{stage_name}.response.json", result)
            check_api_deadline()
            check_deadline()
            if type(result) is not dict:
                raise ValueError("Local inference must return an API object")
            stage.update({k: result.get(k) for k in ("model", "done", "done_reason", "prompt_eval_count",
                                                    "eval_count", "total_duration", "load_duration")})
            adapter.validate_inference_result(result, body["options"])
            stage["inference_validation"] = "accepted"
            if type(result.get("response")) is not str:
                raise ValueError("Local inference response must be a JSON string")
            value = json.loads(result["response"], object_pairs_hook=adapter.unique_response_object)
            check_api_deadline()
            stage["answer"] = value
            return value
        finally:
            stage["seconds"] = time.monotonic() - stage_started
            stage["api_ended_elapsed_seconds"] = time.monotonic() - started

    try:
        directory.mkdir(parents=True, exist_ok=False)
        _write_json(directory / "context.json", context)
        manifest["git_commit"] = _git_commit()
        manifest["source_hashes"] = {}
        for path, name in ((__file__, "wrapper-source.py"), (lookup.__file__, "lookup-source.py"),
                           (adapter.__file__, "adapter-source.py")):
            source = Path(path).resolve()
            manifest["source_hashes"][name] = hashlib.sha256(source.read_bytes()).hexdigest()
            shutil.copyfile(source, directory / name)
        save()
        print(json.dumps(dict(profile=manifest["profile"], audit_directory=str(directory), status="started")),
              file=sys.stderr, flush=True)
        if type(context) is not dict:
            raise ValueError("Lookup input must be a context object")
        adapter.comparison_reference(context)
        manifest["context_sha256"] = lookup.context_fingerprint(context)
        query = call("query", lookup.lookup_request_body(context, args.model, args.max_tokens, **options))
        lookup.validate_lookup(context, query)
        manifest["stages"][-1].update(status="accepted", protocol_validation="accepted")
        manifest["query"] = query
        facts = lookup.materialize_lookup(context, query)
        _write_json(directory / "native-lookup.json", facts)
        save()
        answer = call("choice", lookup.lookup_selection_request_body(context, facts, args.model, args.max_tokens, **options))
        choice = lookup.adapter_owned_lookup_choice(context, facts, answer)
        check_deadline()
        manifest["stages"][-1].update(status="accepted", protocol_validation="accepted")
        manifest.update(status="accepted", choice=choice, accepted_elapsed_seconds=time.monotonic() - started)
    except BaseException as error:
        manifest.update(status="error", error=type(error).__name__ + ": " + str(error))
        if manifest["stages"] and manifest["stages"][-1]["status"] == "running":
            manifest["stages"][-1]["status"] = "error"
        raise
    finally:
        manifest.update(seconds=time.monotonic() - started, ended_utc=datetime.now(timezone.utc).isoformat())
        complete = False
        try:
            if directory.exists():
                save()
                if manifest["status"] == "accepted":
                    check_deadline()
                complete = True
        except BaseException as error:
            manifest.update(status="error", error=type(error).__name__ + ": " + str(error))
            if isinstance(error, OSError):
                manifest["audit_error"] = str(error)
            try:
                save()
            except Exception:
                pass
            print(json.dumps(summary(False)), file=sys.stderr, flush=True)
            raise
        print(json.dumps(summary(complete)), file=sys.stderr, flush=True)
    return choice


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--audit-root", type=Path, default=DEFAULT_AUDIT_ROOT)
    parser.add_argument("--api-timeout", type=int, default=170)
    parser.add_argument("--total-timeout", type=int, default=290)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--context-tokens", type=int, default=8192)
    parser.add_argument("--forecast-format", choices=("rows", "objects", "overrides"), default="overrides")
    parser.add_argument("--temperature", type=float, default=.7)
    parser.add_argument("--top-p", type=float, default=.8)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--min-p", type=float, default=0.)
    args = parser.parse_args()
    if not (1 <= args.api_timeout <= 170 and args.api_timeout <= args.total_timeout <= 290):
        parser.error("Require 1 <= api-timeout <= 170 and api-timeout <= total-timeout <= 290 seconds")
    if not 32 <= args.max_tokens <= 1024 or not 2048 <= args.context_tokens <= 16384:
        parser.error("max-tokens must be 32..1024 and context-tokens 2048..16384")
    if not (0 <= args.temperature <= 2 and 0 < args.top_p <= 1 and 0 <= args.top_k <= 1000 and 0 <= args.min_p <= 1):
        parser.error("Invalid sampling settings")
    tag = args.model.rsplit("/", 1)[-1].lower()
    if tag.startswith("qwen3:") and "-thinking" in tag:
        parser.error("Use an instruct model, not an explicit thinking-only tag")
    context = json.load(sys.stdin, object_pairs_hook=adapter.unique_response_object)
    choice = run_lookup(context, args)
    print(json.dumps(choice))


if __name__ == "__main__":
    main()
