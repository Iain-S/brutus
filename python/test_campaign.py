#!/usr/bin/env python3
"""Load a peaceful campaign mission, audit events, and compare reset traces."""

import argparse
import json
from pathlib import Path

from julius_gym import JuliusEnv
from test_snapshot_restore import observation_digest, run_suffix


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def trace(env, steps):
    observation, info = env.reset()
    terrain, _, width, height = env.get_map_data()
    check(width > 0 and height > 0 and terrain.any(), "Campaign map is empty")
    check(int(observation["victory_population_goal"][0]) > 0, "Missing victory goals")
    states = [(observation_digest(env, observation), info)]
    start_months = int(observation["time_total_months"].item())
    for _ in range(steps):
        observation, reward, terminated, truncated, info = env.step(0)
        states.append((observation_digest(env, observation), reward, terminated, truncated, info))
        check(not terminated and not truncated, "Empty-city smoke episode ended unexpectedly")
    if steps >= 800:
        check(int(observation["time_total_months"].item()) > start_months,
              "Steps did not advance simulation time")
    return states


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--lib-path", type=Path, required=True)
    parser.add_argument("--campaign-rank", type=int, default=3)
    parser.add_argument("--steps", type=int, default=1600)
    args = parser.parse_args()
    if args.steps < 1:
        parser.error("--steps must be positive")
    with_paths = dict(data_directory=str(args.data_dir.resolve()),
                      lib_path=str(args.lib_path.resolve()),
                      campaign_rank=args.campaign_rank, max_ticks=args.steps + 1)
    env = JuliusEnv(**with_paths)
    try:
        first = trace(env, args.steps)
        second = trace(env, args.steps)
        check(first == second, "Campaign reset traces diverged")
        check(env.lib.julius_env_select_campaign(env.env_handle, -1) == -1,
              "C API accepted an invalid campaign rank")
        check(env.lib.julius_env_select_campaign(env.env_handle, 12) == -1,
              "C API accepted an out-of-range campaign rank")
        env.reset()
        run_suffix(env, 4)
        with env.snapshot() as snapshot:
            expected = run_suffix(env, 12)
            snapshot.restore()
            check(expected == run_suffix(env, 12), "Campaign snapshot replay diverged")
        observation, info = env.reset()
        mission = info["mission"]
        check(mission["campaign_rank"] == args.campaign_rank, "Wrong campaign rank")
        check(not mission["is_custom"], "Loaded custom scenario instead of campaign")
        check(not mission["is_tutorial"], "Target still has tutorial behavior")
        if args.campaign_rank == 3:
            check(mission["campaign_mission"] == 4, "Wrong Tarraco mission index")
        goals = {key: int(value[0]) for key, value in observation.items()
                 if key.startswith("victory_")}
        print(json.dumps({"mission": mission, "goals": goals}, indent=2))
        check(not mission["combat_events"] and not mission["gladiator_revolt"],
              "Scheduled combat found; select another peaceful target")
    finally:
        env.close()
    print(f"Campaign audit, {args.steps}-tick reset replay, and snapshot replay passed.")


if __name__ == "__main__":
    main()
