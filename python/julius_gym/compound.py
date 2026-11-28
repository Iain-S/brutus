"""Experimental bounded native plan previews; no live planner policy changes."""

from dataclasses import dataclass

from .env import ActionType as A
from .planner import (Candidate, decision_context, execute_cycle, fingerprint,
                      forecast_state)


@dataclass(frozen=True)
class ShortPlan:
    """Names resolved afresh at each step, bound only to the initial state."""

    state: str
    candidate_ids: tuple

    def __post_init__(self):
        if (not isinstance(self.state, str) or not self.state
                or not isinstance(self.candidate_ids, tuple)
                or not 1 <= len(self.candidate_ids) <= 2
                or any(not isinstance(name, str) or not 1 <= len(name) <= 128
                       for name in self.candidate_ids)):
            raise ValueError("Short plan requires a state and one or two bounded candidate names")


def validate_short_plan(value, context, candidates):
    """Validate model JSON; future names remain conditional on successor legality."""
    if (not isinstance(value, dict)
            or set(value) != {"decision_id", "candidate_ids", "reason"}
            or type(value["decision_id"]) is not int
            or value["decision_id"] != context["decision_id"]
            or not isinstance(value["candidate_ids"], list)
            or not isinstance(value["reason"], str) or len(value["reason"]) > 2000):
        raise ValueError("Short plan must use the exact proposal schema")
    names = tuple(value["candidate_ids"])
    # Validate types before looking up the first name (objects are never actions).
    plan = ShortPlan("pending", names)
    if names[0] not in candidates:
        raise ValueError("First plan step must select a current candidate")
    return ShortPlan(candidates[names[0]].state, plan.candidate_ids)


def native_diagnostics(env):
    """Keep all six raw diagnostic payloads, including staffing and inventories."""
    return {"buildings": env.get_buildings(), "food_supply": env.get_food_supply(),
            "imperial": env.get_imperial_state(), "water_supply": env.get_water_supply(),
            "housing": env.get_housing_state(), "finance": env.get_finance_state()}


def _scalars(observation):
    return {k: int(v.item()) for k, v in observation.items()}


def _finish(env, observation, status, stages, steps, valid):
    ticks = len(steps)
    return {"status": status, "valid": valid, "ticks": ticks,
            "stages": stages, "steps": steps,
            "observation": _scalars(observation),
            "forecast": forecast_state(env, observation, ticks, status),
            "diagnostics": native_diagnostics(env)}


def _rollout(env, plan, observation, mission, budget, minimum_ticks, radius, on_step=None):
    stages, steps = [], []
    status = "completed"
    for index, name in enumerate(plan.candidate_ids):
        remaining = budget - len(steps)
        if not remaining:
            status = "budget_exhausted"
            break
        context, candidates = decision_context(env, observation, mission, index,
                                               remaining, radius=radius, forecast_ticks=0)
        if name not in candidates:
            status = "invalid_successor" if index else "invalid_initial"
            reason = next((row["reason"] for row in context["unavailable"] if row["id"] == name),
                          "Candidate is not available in this state")
            stages.append({"candidate_id": name, "legal": False, "reason": reason,
                           "status": status, "steps": [], "macro_ticks": 0,
                           "observation_ticks": 0})
            break
        before = forecast_state(env, observation, len(steps), "before_step")
        before_observation = _scalars(observation)
        treasury = int(observation["finance_treasury"].item())
        callbacks = {"on_step": on_step} if on_step is not None else {}
        observation, result, terminated, truncated = execute_cycle(
            env, candidates[name], observation, remaining, minimum_ticks, **callbacks)
        steps.extend(result["steps"])
        status = result["status"]
        stages.append({**result, "legal": True, "before": before,
                       "after": forecast_state(env, observation, len(steps), status),
                       "before_observation": before_observation,
                       "after_observation": _scalars(observation),
                       "diagnostics": native_diagnostics(env),
                       "net_treasury_outlay": treasury - int(observation["finance_treasury"].item())})
        if status != "completed" or terminated or truncated:
            break
    valid = status == "won" or (status == "completed" and len(stages) == len(plan.candidate_ids))
    return _finish(env, observation, status, stages, steps, valid)


def _check_entry(env, plan, observation, budget, minimum_ticks):
    if (not isinstance(plan, ShortPlan) or type(budget) is not int or not 1 <= budget <= 8000
            or type(minimum_ticks) is not int or not 0 <= minimum_ticks <= 800):
        raise ValueError("Require a ShortPlan, budget 1..8000 and minimum_ticks 0..800")
    if fingerprint(env, observation) != plan.state:
        raise ValueError("Stale plan: regenerate from current state")
    current = env.get_observation()
    if _scalars(current) != _scalars(observation):
        raise ValueError("Stale observation: read current native state")
    return current


def execute_short_plan(env, plan, observation, mission, budget, minimum_ticks=800, radius=14, on_step=None):
    """Execute checked successor macros; retain live partial progress on failure."""
    observation = _check_entry(env, plan, observation, budget, minimum_ticks)
    return _rollout(env, plan, observation, mission, budget, minimum_ticks, radius, on_step)


def successor_context(env, candidate, observation, mission, decision_id, budget,
                      minimum_ticks=800, forecast_ticks=800, radius=14):
    """Discover a real successor menu, without leaking future candidate objects."""
    observation = _check_entry(env, ShortPlan(candidate.state, (candidate.id,)),
                               observation, budget, minimum_ticks)
    if type(forecast_ticks) is not int or not 0 <= forecast_ticks <= 8000:
        raise ValueError("Successor forecast_ticks must be 0..8000")
    with env.snapshot() as snapshot:
        try:
            after, result, terminated, truncated = execute_cycle(
                env, candidate, observation, budget, minimum_ticks)
            ticks = len(result["steps"])
            if result["status"] != "completed" or terminated or truncated or ticks >= budget:
                raise ValueError("Successor discovery requires a completed nonterminal prefix and remaining budget")
            context, _ = decision_context(env, after, mission, decision_id, budget - ticks,
                                           radius=radius, forecast_ticks=forecast_ticks)
            context["compound_prefix"] = {"candidate_id": candidate.id, "ticks": ticks,
                                          "forecast": forecast_state(env, after, ticks, result["status"]),
                                          "steps": result["steps"], "observation": _scalars(after),
                                          "diagnostics": native_diagnostics(env)}
            return context
        finally:
            snapshot.restore()


def preview_short_plan(env, plan, observation, mission, budget, minimum_ticks=800, radius=14):
    """Simulate a plan and equal-time idle control, restoring the base on every exit.

    The control targets the *actual* ticks of the plan, including an invalid
    prefix. If the control ends early, `equal_time` is false. A comparison is
    usable only when the plan is valid and equal_time is true; no score or
    strategic ranking is assigned here. Exceptions propagate after restoration.
    """
    observation = _check_entry(env, plan, observation, budget, minimum_ticks)
    with env.snapshot() as snapshot:
        try:
            result = _rollout(env, plan, observation, mission, budget, minimum_ticks, radius)
            snapshot.restore()
            ticks = result["ticks"]
            if ticks:
                wait = Candidate("equal_time_wait", [(A.NONE, 0, 0)] * ticks,
                                 fingerprint(env, observation), {})
                after, control, _, _ = execute_cycle(env, wait, observation, ticks)
                control = _finish(env, after, control["status"], [control], control["steps"],
                                  control["status"] in ("completed", "won"))
            else:
                control = _finish(env, observation, "completed", [], [], True)
            return {"candidate_ids": list(plan.candidate_ids), "budget": budget,
                    "minimum_ticks": minimum_ticks, "plan": result, "control": control,
                    "equal_time": result["ticks"] == control["ticks"]}
        finally:
            snapshot.restore()
