"""Fixed-scenario evaluation helpers.

These helpers deliberately report game outcomes separately from the Gym reward.
Reward shaping is useful during training, but a Caesar III result is a win only
when the game reports victory.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np

from .env import ActionType


GOALS = (
    ("population", "population_total", "victory_population_goal"),
    ("culture", "ratings_culture", "victory_culture_goal"),
    ("prosperity", "ratings_prosperity", "victory_prosperity_goal"),
    ("peace", "ratings_peace", "victory_peace_goal"),
    ("favor", "ratings_favor", "victory_favor_goal"),
)


def _scalar(observation: dict[str, Any], key: str) -> int:
    return int(np.asarray(observation[key]).item())


def goal_progress(observation: dict[str, Any]) -> dict[str, dict[str, int | float] | None]:
    """Return current scenario criteria, omitting criteria disabled by the map."""
    result = {}
    for name, value_key, goal_key in GOALS:
        current = _scalar(observation, value_key)
        goal = _scalar(observation, goal_key)
        result[name] = None if goal <= 0 else {
            "current": current,
            "goal": goal,
            "ratio": current / goal,
        }
    return result


def evaluate_action_plan(env, actions: Iterable[tuple[int, int, int]], max_steps: int):
    """Run a finite coordinate-aware plan, then wait until an outcome/boundary.

    ``actions`` consists of ``(action_type, x, y)`` tuples.  Once exhausted,
    the evaluator advances the game with ``ActionType.NONE``.  The returned
    report is JSON serialisable and intentionally records raw game outcome,
    ticks and criteria independently of cumulative reward.
    """
    observation, _ = env.reset()
    action_iter = iter(actions)
    events = []
    total_reward = 0.0
    terminated = truncated = False
    info: dict[str, Any] = {}

    for tick in range(1, max_steps + 1):
        try:
            action, x, y = next(action_iter)
        except StopIteration:
            action, x, y = ActionType.NONE, 0, 0
        observation, reward, terminated, truncated, info = env.step_at(action, x, y)
        total_reward += reward
        if action != ActionType.NONE:
            events.append(
                {
                    "tick": tick,
                    "action": int(action),
                    "x": int(x),
                    "y": int(y),
                    "message": info.get("message", ""),
                    "reward": float(reward),
                }
            )
        if terminated or truncated:
            break

    won = bool(_scalar(observation, "victory_has_won"))
    outcome = "won" if won else "lost" if terminated else "truncated"
    return {
        "outcome": outcome,
        "won": won,
        "terminated": bool(terminated),
        "truncated": bool(truncated),
        "ticks": tick if max_steps else 0,
        "cumulative_reward": float(total_reward),
        "last_message": info.get("message", ""),
        "goals": goal_progress(observation),
        "actions": events,
    }
