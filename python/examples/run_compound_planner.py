#!/usr/bin/env python3
"""Small audited native experiment with sequential model-proposed two-step plans."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from julius_gym import JuliusEnv
from julius_gym.compound import (ShortPlan, execute_short_plan, preview_short_plan,
                                 successor_context)
from julius_gym.planner import decision_context, fingerprint
from julius_gym.run_artifacts import DEFAULT_RUNS, RunArtifacts
import compound_planner as protocol
import ollama_planner as adapter

MODEL = "qwen3:4b-instruct-2507-q4_K_M"
MODEL_DIGEST = "0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0"


def verify_model():
    with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=10) as response:
        models = json.load(response, object_pairs_hook=adapter.unique_response_object)
    if not any(model["name"] == MODEL and model["digest"] == MODEL_DIGEST for model in models["models"]):
        raise RuntimeError("The pinned instruct model and digest must already be installed")
    return MODEL_DIGEST


def verify_delivery(expected, actual):
    for key in ("steps", "ticks", "status", "valid", "observation", "forecast", "diagnostics"):
        if protocol.canonical(expected[key]) != protocol.canonical(actual[key]):
            raise RuntimeError(f"Delivered compound outcome differs from preview: {key}")
    # The wait control has one 1600-tick stage; live waiting has two cycles.
    if expected.get("stages") and "after" in expected["stages"][0]:
        if protocol.canonical(expected["stages"]) != protocol.canonical(actual["stages"]):
            raise RuntimeError("Delivered per-stage diagnostics differ from preview")


def run_decision(env, observation, mission, decision_id, budget, directory, model, on_step):
    directory.mkdir(exist_ok=False)
    record = {"decision_id": decision_id, "status": "running", "fallbacks": 0,
              "proposal_valid": False, "forecast_reliable": False,
              "execution_verified": False, "strategic_improvement": "not_established"}
    started = time.monotonic()
    try:
        initial = fingerprint(env, observation)
        context, candidates = decision_context(env, observation, mission, decision_id, budget, forecast_ticks=800)
        context["elapsed_ticks"] = 8000 - budget
        context["minimum_decision_interval"] = 800
        protocol.write_json(directory / "first.context.json", context)
        value = model.call("first", protocol.proposal_request(context, MODEL, "first"),
                           lambda answer: protocol.validate_proposal(answer, context))
        first = protocol.validate_proposal(value, context)
        record["first_proposal"] = value
        successor = successor_context(env, candidates[first], observation, mission, decision_id, budget)
        successor["elapsed_ticks"] = context["elapsed_ticks"] + successor["compound_prefix"]["ticks"]
        successor["minimum_decision_interval"] = 800
        protocol.write_json(directory / "successor.context.json", successor)
        value = model.call("successor", protocol.proposal_request(successor, MODEL, "successor"),
                           lambda answer: protocol.validate_proposal(answer, successor))
        second = protocol.validate_proposal(value, successor)
        record["successor_proposal"] = value
        record["proposal_valid"] = True
        names = {"compound": (first, second), "single": (first, "wait"), "wait": ("wait", "wait")}
        proposal = {"candidate_ids": [first, second], "successor": successor}
        protocol.write_json(directory / "proposal.json", proposal)
        previews = {name: preview_short_plan(env, ShortPlan(initial, ids), observation, mission, budget)
                    for name, ids in names.items() if name != "wait"}
        protocol.write_json(directory / "previews.json", previews)
        facts = protocol.comparison(context, previews, proposal)
        protocol.write_json(directory / "comparison.json", facts)
        if fingerprint(env, env.get_observation()) != initial:
            raise RuntimeError("Planning did not restore the native base state")
        record["forecast_reliable"] = True
        selection = model.call("selection", protocol.selection_request(context, previews, proposal, MODEL),
                               lambda answer: protocol.validate_selection(answer, context, previews, proposal))
        selected = protocol.validate_selection(selection, context, previews, proposal)
        expected = previews[selected]["plan"] if selected != "wait" else previews["compound"]["control"]
        record.update(selected=selected, selected_candidate_ids=list(names[selected]),
                      selection=selection, evidence_origin="native_adapter",
                      comparison_sha256=protocol.digest(facts))
        # Persist the accepted exact proposal/selection before live native effects.
        protocol.write_json(directory / "decision.json", record)
        actual = execute_short_plan(env, ShortPlan(initial, names[selected]), observation, mission,
                                    budget, on_step=on_step)
        protocol.write_json(directory / "actual.json", actual)
        verify_delivery(expected, actual)
        record.update(status="completed", execution_verified=True, ticks=actual["ticks"])
        return actual
    except BaseException as error:
        record.update(status="error", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        record["seconds"] = time.monotonic() - started
        protocol.write_json(directory / "decision.json", record)


def finalize(artifacts, env, ticks, completed, primary_error):
    """Attempt final saves and cleanup even if audit aggregation/diagnostics fail."""
    errors, calls, responses = [], 0, 0
    unknown_counts = False
    try:
        for path in artifacts.directory.glob("decision-*/*.audit.json"):
            try:
                audit = json.loads(path.read_text(encoding="utf-8"))
                calls += audit["api_calls"]
                responses += audit["api_responses"]
            except Exception as failure:
                errors.append(f"{path.name}: {failure}")
                unknown_counts = True
        observation, won = {}, False
        if env is not None and artifacts.ready:
            try:
                observation = env.get_observation()
                won = env.get_victory_state() == 1
            except Exception as failure:
                errors.append(f"final observation/victory: {failure}")
        summary = {"ticks": ticks, "completed_decisions": completed,
                   "api_calls": None if unknown_counts else calls,
                   "api_responses": None if unknown_counts else responses, "retries": 0, "fallbacks": 0,
                   "population": int(observation["population_total"].item()) if observation else None,
                   "observation": {k: int(v.item()) for k, v in observation.items()}, "won": won,
                   "stop_reason": "error" if primary_error or errors else "decision_budget",
                   "strategic_improvement": "not_established"}
        artifacts.metadata["finalization_errors"] = errors
        error = primary_error or (RuntimeError("Finalization errors: " + "; ".join(errors)) if errors else None)
        artifacts.finish(env, summary, error)
        if error is not None and primary_error is None:
            raise error
    finally:
        if env is not None:
            env.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--lib-path", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--max-decisions", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.max_decisions <= 4:
        parser.error("max-decisions must be 1..4")
    data, library = args.data_dir.resolve(), args.lib_path.resolve()
    artifacts = RunArtifacts("compound-model", args.runs_dir, configuration={
        "max_ticks": 8000, "max_decisions": args.max_decisions, "minimum_cycle_ticks": 800,
        "model": MODEL, "model_digest": MODEL_DIGEST, "options": protocol.OPTIONS,
        "max_tokens": 256, "per_api_deadline": 170, "retries": 0, "fallbacks": 0,
        "protocol": "sequential-root-successor-selection-v1"})
    directory = artifacts.directory
    package = Path(__file__).resolve().parents[1] / "julius_gym"
    sources = (Path(__file__).resolve(), Path(protocol.__file__), Path(adapter.__file__),
               package / "compound.py", package / "planner.py", package / "env.py")
    source_dir = directory / "source"
    source_dir.mkdir()
    artifacts.metadata["source_sha256"] = {}
    for source in sources:
        content = source.read_bytes()
        (source_dir / source.name).write_bytes(content)
        artifacts.metadata["source_sha256"][source.name] = hashlib.sha256(content).hexdigest()
    artifacts.metadata["library_sha256"] = hashlib.sha256(library.read_bytes()).hexdigest()
    env = None
    ticks = completed = 0
    try:
        artifacts.metadata["model_digest_before"] = verify_model()
        env = JuliusEnv(data_directory=str(data), lib_path=str(library), campaign_rank=3, max_ticks=8000)
        observation, info = env.reset()
        artifacts.ready = True
        mission = info["mission"]
        artifacts.metadata["mission"] = mission
        if mission["is_tutorial"] or mission["combat_events"] or mission["gladiator_revolt"]:
            raise RuntimeError("Compound experiment requires a peaceful non-tutorial mission")
        with artifacts.log.open("w", encoding="utf-8") as log:
            def record_step(step):
                nonlocal ticks
                ticks += 1
                log.write(json.dumps({"tick": ticks, **step}, allow_nan=False) + "\n")
                log.flush()
            for decision_id in range(args.max_decisions):
                child = directory / f"decision-{decision_id:02d}"
                model = protocol.AuditedModel(child, MODEL)
                result = run_decision(env, observation, mission, decision_id, 8000 - ticks,
                                      child, model, record_step)
                completed += 1
                observation = env.get_observation()
                print(json.dumps({"decision": decision_id, "ticks": ticks,
                                  "forecast_delivered": True, "forecast": result["forecast"]}), flush=True)
        artifacts.metadata["model_digest_after"] = verify_model()
    finally:
        finalize(artifacts, env, ticks, completed, sys.exc_info()[1])


if __name__ == "__main__":
    main()
