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
    digest.update(f"{id(env)}:{env.get_state_token()}".encode())
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
    victory = env.get_victory_state() if terminated else 0
    status = ("won" if victory == 1 else "lost" if victory == -1 else "failed" if failed
              else "terminated" if terminated else "truncated" if truncated
              else "completed" if len(records) == len(candidate.actions) else "budget_exhausted")
    return observation, {"candidate_id": candidate.id, "status": status, "steps": records}, terminated, truncated


def preview_is_usable(result):
    return result["status"] in ("completed", "won")


def forecast_state(env, observation, ticks, status):
    buildings = env.get_buildings()
    return {"ticks": ticks, "status": status,
            "population": int(observation["population_total"].item()),
            "culture": int(observation["ratings_culture"].item()),
            "treasury": int(observation["finance_treasury"].item()),
            "food_stocks": int(observation["resources_food_stocks"].item()),
            "residents_with_food": sum(b["population"] for b in buildings if b["food"] > 0),
            "health": env.get_population_info()["health"],
            "farm_workers": sum(b["workers"] for b in buildings if b["type"] == 100)}


def preview_candidate(env, candidate, observation, budget, forecast_ticks=0):
    """Validate construction, optionally continue without further building, then roll back."""
    with env.snapshot() as snapshot:
        try:
            after, result, terminated, truncated = execute(env, candidate, observation, budget)
            outlay = int(observation["finance_treasury"].item() - after["finance_treasury"].item())
            forecast = None
            if forecast_ticks and (preview_is_usable(result) or candidate.id == "wait"):
                ticks = len(result["steps"])
                status = result["status"]
                wait_ticks = min(max(0, forecast_ticks - ticks), max(0, budget - ticks))
                if wait_ticks and not terminated and not truncated:
                    wait = Candidate("forecast_wait", [(A.NONE, 0, 0)] * wait_ticks,
                                     fingerprint(env, after), {})
                    after, continued, _, _ = execute(env, wait, after, wait_ticks)
                    ticks += len(continued["steps"])
                    status = continued["status"]
                forecast = forecast_state(env, after, ticks, status)
        finally:
            snapshot.restore()
    return result, outlay, forecast


def execute_cycle(env, candidate, observation, budget, minimum_ticks=0):
    """Optionally observe effects before the next model call; charge every tick."""
    observation, result, terminated, truncated = execute(env, candidate, observation, budget)
    macro_ticks = len(result["steps"])
    result["macro_ticks"] = macro_ticks
    result["observation_ticks"] = 0
    if result["status"] != "completed" or terminated or truncated:
        return observation, result, terminated, truncated
    wait_ticks = min(max(0, minimum_ticks - macro_ticks), max(0, budget - macro_ticks))
    if wait_ticks:
        wait = Candidate("observe_effects", [(A.NONE, 0, 0)] * wait_ticks,
                         fingerprint(env, observation), {})
        observation, observed, terminated, truncated = execute(env, wait, observation, wait_ticks)
        result["steps"].extend(observed["steps"])
        result["observation_ticks"] = len(observed["steps"])
        result["status"] = observed["status"]
    if result["status"] == "completed" and len(result["steps"]) < minimum_ticks:
        result["status"] = "budget_exhausted"
    return observation, result, terminated, truncated


def connect_if_needed(make_farm, make_bridge):
    """A farmland connection is useful only when a farm site is not reachable."""
    try:
        make_farm()
    except RuntimeError:
        return make_bridge()
    raise RuntimeError("Farmland is already reachable; a new bridge is not required")


def food_supply_plan(env, mission, radius):
    """Compose a food district against successive map states, then roll it back."""
    actions = []
    home = next(((b["x"], b["y"]) for b in env.get_buildings() if b["level"] >= 0), None)

    def current_map():
        terrain, buildings, width, height = env.get_map_data()
        return exclude_hazard(terrain, mission["earthquake"], radius), buildings, width, height

    def apply(phase):
        for action in phase:
            if len(actions) >= 128:
                raise RuntimeError("Food supply macro exceeds 128-action bound")
            actions.append(action)
            _, _, terminated, truncated, info = env.step_at(*action)
            if terminated or truncated:
                return True
            if not info["message"].startswith("Built "):
                raise RuntimeError("Food supply preflight: " + info["message"])
        return False

    with env.snapshot() as snapshot:
        try:
            try:
                farm_plan = building_plan(*current_map(), mission["entry"], A.BUILD_WHEAT_FARM, 3, True)
            except RuntimeError:
                if apply(bridge_plan(env, mission["entry"], mission["earthquake"], radius)):
                    return actions
                farm_plan = building_plan(*current_map(), mission["entry"], A.BUILD_WHEAT_FARM, 3, True)
            farm = farm_plan[-1][1:]
            if apply(farm_plan):
                return actions
            workers = starter_plan(*current_map(), mission["entry"], anchor=farm)
            if home is None:
                home = next((x, y) for kind, x, y in workers if kind == A.BUILD_HOUSING)
            if apply(workers):
                return actions
            for kind, size, anchor in ((A.BUILD_GRANARY, 3, farm), (A.BUILD_MARKET, 2, home),
                                       (A.BUILD_PREFECTURE, 1, farm), (A.BUILD_ENGINEERS_POST, 1, farm)):
                if apply(building_plan(*current_map(), mission["entry"], kind, size, anchor=anchor)):
                    return actions
            return actions
        finally:
            snapshot.restore()


def proposals(env, mission, radius):
    terrain, buildings, width, height = env.get_map_data()
    terrain = exclude_hazard(terrain, mission["earthquake"], radius)
    entry = mission["entry"]
    yield "expand_housing", lambda: starter_plan(terrain, buildings, width, height, entry)
    make_farm = lambda: building_plan(terrain, buildings, width, height, entry, A.BUILD_WHEAT_FARM, 3, True)
    yield "connect_farmland", lambda: connect_if_needed(make_farm, lambda: bridge_plan(env, entry, mission["earthquake"], radius))
    yield "add_wheat_farm", make_farm
    records = env.get_buildings()
    if not any(b["type"] == 100 for b in records):
        yield "establish_wheat_supply", lambda: food_supply_plan(env, mission, radius)
    for farm in (b for b in records if b["type"] == 100):
        anchor = farm["x"], farm["y"]
        yield f"house_farm_workers_{farm['id']}", lambda anchor=anchor: starter_plan(
            terrain, buildings, width, height, entry, anchor=anchor)
        for name, kind in (("prefecture", A.BUILD_PREFECTURE), ("engineers", A.BUILD_ENGINEERS_POST)):
            yield f"protect_farm_{farm['id']}_{name}", lambda anchor=anchor, kind=kind: building_plan(
                terrain, buildings, width, height, entry, kind, 1, anchor=anchor)
    anchors = []
    for b in records:
        if b["type"] == 92 and all(abs(b["x"] - x) + abs(b["y"] - y) > 6 for x, y in anchors):
            anchors.append((b["x"], b["y"]))
    for index, anchor in enumerate(anchors[:4]):
        for name, kind, size in (("market", A.BUILD_MARKET, 2), ("granary", A.BUILD_GRANARY, 3),
                                 ("doctor", A.BUILD_DOCTOR, 1), ("temple", A.BUILD_TEMPLE_SMALL, 2),
                                 ("school", A.BUILD_SCHOOL, 2), ("library", A.BUILD_LIBRARY, 2),
                                 ("theater", A.BUILD_THEATER, 2), ("actor_colony", A.BUILD_ACTOR_COLONY, 3)):
            yield f"add_{name}_district_{index}", lambda kind=kind, size=size, anchor=anchor: building_plan(
                terrain, buildings, width, height, entry, kind, size, anchor=anchor)


def decision_context(env, observation, mission, decision_id, budget, last_result=None, radius=14,
                     forecast_ticks=0):
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
        result, outlay, forecast = preview_candidate(env, candidate, observation, budget, forecast_ticks)
        if not preview_is_usable(result):
            unavailable.append({"id": name, "reason": result["steps"][-1]["message"]})
            continue
        candidate.preview = {"ticks": len(result["steps"]), "planned_ticks": len(actions), "net_treasury_outlay": outlay,
                             "action_counts": dict(Counter(str(a[0]) for a in actions)),
                             "target": actions[-1], "engine_preview_passed": True,
                             "preview_outcome": result["status"]}
        if name == "establish_wheat_supply":
            candidate.preview["benefit"] = "farm, worker housing, granary and market"
        if forecast is not None:
            candidate.preview["forecast"] = forecast
        candidates[name] = candidate
    wait = Candidate("wait", [(A.NONE, 0, 0)] * min(800, budget), state, {})
    wait.preview = {"ticks": len(wait.actions)}
    if forecast_ticks:
        _, _, forecast = preview_candidate(env, wait, observation, budget, forecast_ticks)
        wait.preview["forecast"] = forecast
    candidates["wait"] = wait
    buildings = env.get_buildings()
    scalar = {k: int(v.item()) for k, v in observation.items()}
    context = {"decision_id": decision_id, "objective": "Win Tarraco in minimum simulation ticks",
               "rules": "Choose one listed candidate_id. Return JSON decision_id, candidate_id, reason only.",
               "remaining_ticks": budget, "state": scalar, "mission": mission,
               "services": {"residents_with_food": sum(b["population"] for b in buildings if b["food"] > 0),
                            "residents_with_water": sum(b["population"] for b in buildings if b["well"] or b["fountain"]),
                            "health": env.get_population_info()["health"],
                            "markets": sum(b["type"] == 70 for b in buildings),
                            "staffed_markets": sum(b["type"] == 70 and b["workers"] > 0 for b in buildings),
                            "granaries": sum(b["type"] == 71 for b in buildings),
                            "staffed_granaries": sum(b["type"] == 71 and b["workers"] > 0 for b in buildings),
                            "ceres_temples": sum(b["type"] == 60 for b in buildings),
                            "schools": sum(b["type"] == 51 for b in buildings),
                            "libraries": sum(b["type"] == 53 for b in buildings),
                            "theaters": sum(b["type"] == 31 for b in buildings),
                            "actor_colonies": sum(b["type"] == 36 for b in buildings),
                            "farms": sum(b["type"] == 100 for b in buildings),
                            "farm_workers": sum(b["workers"] for b in buildings if b["type"] == 100),
                            "farms_without_labor_coverage": sum(b["type"] == 100 and b["houses_covered"] == 0 for b in buildings)},
               "candidates": [{"id": c.id, **c.preview} for c in candidates.values()],
               "unavailable": unavailable,
               "last_result": ({"candidate_id": last_result.get("candidate_id"),
                                "status": last_result["status"], "executed_ticks": len(last_result["steps"]),
                                "final_step": last_result["steps"][-1] if last_result["steps"] else None}
                               if last_result else None),
               "limitations": ["Food production/consumption monthly fields are placeholders",
                               "Quake buffer is heuristic; service coverage is not guaranteed by placement",
                               "Only Ceres temples and a small action vocabulary are currently supported"]}
    if forecast_ticks:
        context["forecast_policy"] = {"minimum_ticks": forecast_ticks,
                                      "continuation": "No further construction; remaining episode budget applies"}
    return context, candidates


def validate_choice(value, context, candidates):
    if (not isinstance(value, dict) or set(value) != {"decision_id", "candidate_id", "reason"}
            or type(value["decision_id"]) is not int
            or value["decision_id"] != context["decision_id"]
            or not isinstance(value["candidate_id"], str) or value["candidate_id"] not in candidates
            or not isinstance(value["reason"], str) or len(value["reason"]) > 2000):
        raise ValueError("Planner response must select a current candidate using the exact JSON schema")
    return candidates[value["candidate_id"]]


def command_choice(command, context, timeout=60, audit=None):
    """One process per decision; bounded response time and output size."""
    try:
        result = subprocess.run(command, input=json.dumps(context), text=True, capture_output=True,
                                encoding="utf-8", errors="replace", timeout=timeout, shell=False)
    except subprocess.TimeoutExpired as error:
        if audit is not None:
            def decoded(value):
                return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""
            audit.append({"timed_out": True, "stdout": decoded(error.stdout)[:16384],
                          "stderr": decoded(error.stderr)[:2048]})
        raise
    if audit is not None:
        audit.append({"returncode": result.returncode, "stdout": result.stdout[:16384],
                      "stderr": result.stderr[:2048]})
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
