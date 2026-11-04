"""Bounded JSON planning over engine-tested macros. No model SDK required."""

from dataclasses import dataclass
import hashlib
import json
import subprocess
from collections import Counter

from .baseline import bridge_plan, building_plan, exclude_hazard, starter_plan
from .env import ActionType as A


def fingerprint(env, observation):
    digest = hashlib.sha256(json.dumps({k: int(v.item()) for k, v in observation.items()},
                                     sort_keys=True).encode())
    terrain, buildings, width, height = env.get_map_data()
    digest.update(f"{width},{height}".encode())
    digest.update(terrain.tobytes())
    digest.update(buildings.tobytes())
    return digest.hexdigest()


@dataclass
class Candidate:
    id: str
    actions: list
    state: str
    preview: dict


def execute(env, candidate, observation, budget):
    """Execute a macro, retaining and reporting partial progress on failure."""
    if fingerprint(env, observation) != candidate.state:
        raise ValueError("Stale candidate: regenerate from current state")
    records = []
    terminated = truncated = False
    for action in candidate.actions[:budget]:
        observation, reward, terminated, truncated, info = env.step_at(*action)
        record = {"action": action, "reward": reward, **info}
        records.append(record)
        failed = (not terminated and not truncated and action[0] >= A.BUILD_HOUSING
                  and not info["message"].startswith("Built "))
        if failed or terminated or truncated:
            break
    else:
        failed = False
    status = ("failed" if failed else "terminated" if terminated else "truncated" if truncated
              else "completed" if len(records) == len(candidate.actions) else "budget_exhausted")
    return observation, {"status": status, "steps": records}, terminated, truncated


def proposals(env, mission, radius):
    terrain, buildings, width, height = env.get_map_data()
    terrain = exclude_hazard(terrain, mission["earthquake"], radius)
    entry = mission["entry"]
    yield "expand_housing", lambda: starter_plan(terrain, buildings, width, height, entry)
    yield "connect_farmland", lambda: bridge_plan(env, entry, mission["earthquake"], radius)
    yield "add_wheat_farm", lambda: building_plan(terrain, buildings, width, height, entry, A.BUILD_WHEAT_FARM, 3, True)
    records = env.get_buildings()
    anchors = []
    for b in records:
        if b["type"] == 92 and all(abs(b["x"] - x) + abs(b["y"] - y) > 6 for x, y in anchors):
            anchors.append((b["x"], b["y"]))
    for index, anchor in enumerate(anchors[:4]):
        for name, kind, size in (("market", A.BUILD_MARKET, 2), ("granary", A.BUILD_GRANARY, 3),
                                 ("doctor", A.BUILD_DOCTOR, 1), ("temple", A.BUILD_TEMPLE_SMALL, 2)):
            yield f"add_{name}_district_{index}", lambda kind=kind, size=size, anchor=anchor: building_plan(
                terrain, buildings, width, height, entry, kind, size, anchor=anchor)


def decision_context(env, observation, mission, decision_id, budget, last_result=None, radius=14):
    """Dry-run candidates in snapshots; retain only engine-successful macros.

    Preview treasury change includes any simulation income/expenses during the
    macro. It is an observed net outlay, not a construction-price quotation.
    """
    state = fingerprint(env, observation)
    candidates, unavailable = {}, []
    for name, make_actions in proposals(env, mission, radius):
        try:
            actions = make_actions()
        except RuntimeError as error:
            unavailable.append({"id": name, "reason": str(error)})
            continue
        if not actions or len(actions) > min(128, budget):
            unavailable.append({"id": name, "reason": "Macro exceeds remaining action budget"})
            continue
        candidate = Candidate(name, actions, state, {})
        with env.snapshot() as snapshot:
            try:
                after, result, terminated, truncated = execute(env, candidate, observation, budget)
                outlay = int(observation["finance_treasury"].item() - after["finance_treasury"].item())
            finally:
                snapshot.restore()
        if result["status"] != "completed":
            unavailable.append({"id": name, "reason": result["steps"][-1]["message"]})
            continue
        candidate.preview = {"ticks": len(actions), "net_treasury_outlay": outlay,
                             "action_counts": dict(Counter(str(a[0]) for a in actions)),
                             "target": actions[-1], "engine_preview_passed": True}
        candidates[name] = candidate
    wait = Candidate("wait", [(A.NONE, 0, 0)] * min(800, budget), state, {})
    wait.preview = {"ticks": len(wait.actions)}
    candidates["wait"] = wait
    buildings = env.get_buildings()
    scalar = {k: int(v.item()) for k, v in observation.items()}
    context = {"decision_id": decision_id, "objective": "Win Tarraco in minimum simulation ticks",
               "rules": "Choose one listed candidate_id. Return JSON decision_id, candidate_id, reason only.",
               "remaining_ticks": budget, "state": scalar, "mission": mission,
               "services": {"residents_with_food": sum(b["population"] for b in buildings if b["food"] > 0),
                            "residents_with_water": sum(b["population"] for b in buildings if b["well"] or b["fountain"])},
               "candidates": [{"id": c.id, **c.preview} for c in candidates.values()],
               "unavailable": unavailable,
               "last_result": ({"status": last_result["status"], "executed_ticks": len(last_result["steps"]),
                                "final_step": last_result["steps"][-1] if last_result["steps"] else None}
                               if last_result else None),
               "limitations": ["Food production/consumption monthly fields are placeholders",
                               "Quake buffer is heuristic; service coverage is not guaranteed by placement",
                               "Only Ceres temples and a small action vocabulary are currently supported"]}
    return context, candidates


def validate_choice(value, context, candidates):
    if (not isinstance(value, dict) or set(value) != {"decision_id", "candidate_id", "reason"}
            or type(value["decision_id"]) is not int
            or value["decision_id"] != context["decision_id"]
            or not isinstance(value["candidate_id"], str) or value["candidate_id"] not in candidates
            or not isinstance(value["reason"], str) or len(value["reason"]) > 2000):
        raise ValueError("Planner response must select a current candidate using the exact JSON schema")
    return candidates[value["candidate_id"]]


def command_choice(command, context, timeout=60):
    """One process per decision; bounded response time and output size."""
    result = subprocess.run(command, input=json.dumps(context), text=True, capture_output=True,
                            encoding="utf-8", errors="replace", timeout=timeout, shell=False)
    if result.returncode:
        raise ValueError("Model command failed (nonzero exit status)")
    if len(result.stdout) > 16384:
        raise ValueError("Model response exceeds 16 KiB")
    return json.loads(result.stdout)


def rule_choice(context, candidates):
    """Executor smoke policy, deliberately limited; not an LLM substitute."""
    if context["decision_id"] == 0 and "expand_housing" in candidates:
        name = "expand_housing"
    else:
        name = "wait"
    return {"decision_id": context["decision_id"], "candidate_id": name, "reason": "Executor smoke policy"}
