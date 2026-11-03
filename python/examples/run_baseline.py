#!/usr/bin/env python3
"""Build a deterministic Tarraco starter settlement and measure immigration."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from julius_gym import JuliusEnv
from julius_gym.baseline import starter_plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--lib-path", required=True, type=Path)
    parser.add_argument("--max-ticks", type=int, default=3000)
    parser.add_argument("--log", type=Path, default=Path("runs/baseline.jsonl"))
    args = parser.parse_args()
    if args.max_ticks < 100:
        parser.error("--max-ticks must be at least 100")
    log_path = args.log.resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    env = JuliusEnv(data_directory=str(args.data_dir.resolve()),
                    lib_path=str(args.lib_path.resolve()), campaign_rank=3,
                    max_ticks=args.max_ticks)
    try:
        obs, info = env.reset()
        mission = info["mission"]
        if mission["is_tutorial"] or mission["combat_events"] or mission["gladiator_revolt"]:
            raise RuntimeError("Target is unsuitable for this peaceful baseline")
        terrain, buildings, width, height = env.get_map_data()
        actions = starter_plan(terrain, buildings, width, height, mission["entry"])
        initial_population = int(obs["population_total"].item())
        peak_population = initial_population
        failed = 0
        with log_path.open("w", encoding="utf-8") as log:
            log.write(json.dumps({"mission": mission, "planned_actions": len(actions)}) + "\n")
            for tick in range(args.max_ticks):
                action = actions[tick] if tick < len(actions) else (0, 0, 0)
                treasury = int(obs["finance_treasury"].item())
                obs, reward, terminated, truncated, result = env.step_at(*action)
                population = int(obs["population_total"].item())
                peak_population = max(peak_population, population)
                if action[0] and not result["message"].startswith("Built "):
                    failed += 1
                    raise RuntimeError(f"Placement failed at tick {tick + 1}: {action}: {result}")
                if action[0] and int(obs["finance_treasury"].item()) >= treasury:
                    raise RuntimeError("Successful construction did not charge treasury")
                log.write(json.dumps({"tick": tick + 1, "action": action,
                    "population": population, "treasury": int(obs["finance_treasury"].item()),
                    "reward": reward, "terminated": terminated, "truncated": truncated,
                    **result}) + "\n")
                if terminated or truncated:
                    break
        summary = {"ticks": tick + 1, "population": population,
                   "peak_population": peak_population, "failed_actions": failed,
                   "won": bool(obs["victory_has_won"].item()), "log": str(log_path)}
        print(json.dumps(summary, indent=2))
        if peak_population <= initial_population:
            raise RuntimeError("Starter settlement did not attract immigrants")
    finally:
        env.close()


if __name__ == "__main__":
    main()
