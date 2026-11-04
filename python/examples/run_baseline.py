#!/usr/bin/env python3
"""Build a deterministic Tarraco starter settlement and measure immigration."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from julius_gym import JuliusEnv
from julius_gym.env import ActionType
from julius_gym.baseline import bridge_plan, building_plan, exclude_hazard, starter_plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--lib-path", required=True, type=Path)
    parser.add_argument("--max-ticks", type=int, default=3000)
    parser.add_argument("--log", type=Path, default=Path("runs/baseline.jsonl"))
    parser.add_argument("--food", action="store_true", help="Add a farm, granary and market")
    parser.add_argument("--health", action="store_true", help="Add local doctors to the food baseline")
    parser.add_argument("--quake-buffer", type=int, default=0, help="Avoid new land construction within this radius of the quake origin")
    parser.add_argument("--blocks", type=int, default=1, help="Number of starter housing blocks")
    args = parser.parse_args()
    if args.max_ticks < 100:
        parser.error("--max-ticks must be at least 100")
    if args.quake_buffer < 0:
        parser.error("--quake-buffer must be nonnegative")
    if args.health and not args.food:
        parser.error("--health currently requires --food")
    if not 1 <= args.blocks <= 8:
        parser.error("--blocks must be from 1 to 8")
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
        terrain = exclude_hazard(terrain, mission["earthquake"], args.quake_buffer)
        actions = starter_plan(terrain, buildings, width, height, mission["entry"])
        home = next((x, y) for kind, x, y in actions if kind == ActionType.BUILD_HOUSING)
        farm = None
        phases = [None] * (args.blocks - 1)
        if args.food:
            phases += ["bridge", (ActionType.BUILD_WHEAT_FARM, 3, True),
                       "workers",
                       (ActionType.BUILD_GRANARY, 3, False),
                       (ActionType.BUILD_MARKET, 2, False), "supply"]
        initial_population = int(obs["population_total"].item())
        peak_population = initial_population
        failed = 0
        supply = {}
        previous_buildings = {}
        with log_path.open("w", encoding="utf-8") as log:
            log.write(json.dumps({"mission": mission, "planned_actions": len(actions)}) + "\n")
            for tick in range(args.max_ticks):
                while tick == len(actions) and phases:
                    phase = phases.pop(0)
                    terrain, buildings, width, height = env.get_map_data()
                    terrain = exclude_hazard(terrain, mission["earthquake"], args.quake_buffer)
                    if phase is None:
                        actions += starter_plan(terrain, buildings, width, height, mission["entry"])
                    elif phase == "bridge":
                        actions += bridge_plan(env, mission["entry"], mission["earthquake"], args.quake_buffer)
                    elif phase == "workers":
                        actions += starter_plan(terrain, buildings, width, height,
                                                mission["entry"], anchor=farm)
                    elif phase == "supply":
                        # One local market per housing block; mobile sellers may miss
                        # branches of the shared entry road for long periods.
                        records = env.get_buildings()
                        wells = []
                        for b in records:
                            if b["type"] == 92 and all(abs(b["x"] - x) + abs(b["y"] - y) > 6 for x, y in wells):
                                wells.append((b["x"], b["y"]))
                        phases = [(ActionType.BUILD_PREFECTURE, 1, False, farm),
                                  (ActionType.BUILD_ENGINEERS_POST, 1, False, farm)] + [
                            (ActionType.BUILD_MARKET, 2, False, well) for well in wells] + phases
                        if args.health:
                            phases = [(ActionType.BUILD_DOCTOR, 1, False, well) for well in wells] + phases
                    else:
                        kind, size, meadow = phase[:3]
                        anchor = phase[3] if len(phase) > 3 else (
                            None if meadow else farm if kind == ActionType.BUILD_GRANARY else home)
                        planned = building_plan(terrain, buildings, width, height,
                                                mission["entry"], kind, size, meadow,
                                                anchor=anchor)
                        actions += planned
                        if kind == ActionType.BUILD_WHEAT_FARM:
                            farm = planned[-1][1:]
                action = actions[tick] if tick < len(actions) else (0, 0, 0)
                treasury = int(obs["finance_treasury"].item())
                obs, reward, terminated, truncated, result = env.step_at(*action)
                population = int(obs["population_total"].item())
                peak_population = max(peak_population, population)
                changes = []
                if tick % 50 == 0 or terminated or truncated:
                    buildings = env.get_buildings()
                    current_buildings = {b["id"]: b for b in buildings}
                    changes = [{**b, "replacement": current_buildings.get(bid)} for bid, b in previous_buildings.items()
                               if bid not in current_buildings or current_buildings[bid]["type"] == 99
                               and b["type"] != 99]
                    previous_buildings = current_buildings
                    supply = {
                        "supply_sample_tick": tick + 1,
                        **env.get_population_info(),
                        "residents_with_food": sum(b["population"] for b in buildings if b["food"] > 0),
                        "residents_with_water": sum(b["population"] for b in buildings if b["well"] or b["fountain"]),
                        "occupied_houses": sum(b["population"] > 0 for b in buildings),
                        "farms": sum(b["type"] == 100 for b in buildings),
                    }
                construction = action[0] >= ActionType.BUILD_HOUSING
                if construction and not result["message"].startswith("Built "):
                    failed += 1
                    raise RuntimeError(f"Placement failed at tick {tick + 1}: {action}: {result}")
                if construction and int(obs["finance_treasury"].item()) >= treasury:
                    raise RuntimeError("Successful construction did not charge treasury")
                log.write(json.dumps({"tick": tick + 1, "action": action,
                    "population": population, "treasury": int(obs["finance_treasury"].item()),
                    "food_stocks": int(obs["resources_food_stocks"].item()),
                    "sentiment": int(obs["population_sentiment"].item()),
                    "tax": int(obs["finance_tax_percentage"].item()),
                    "unemployment": int(obs["labor_unemployment_pct"].item()),
                    **supply,
                    "removed_buildings": changes,
                    "reward": reward, "terminated": terminated, "truncated": truncated,
                    **result}) + "\n")
                if terminated or truncated:
                    break
        summary = {"ticks": tick + 1, "population": population,
                   "peak_population": peak_population, "failed_actions": failed,
                   "food_stocks": int(obs["resources_food_stocks"].item()),
                   **supply,
                   "diagnostics": str(log_path.with_suffix(".buildings.json")),
                   "won": bool(obs["victory_has_won"].item()), "log": str(log_path)}
        print(json.dumps(summary, indent=2))
        log_path.with_suffix(".buildings.json").write_text(
            json.dumps(env.get_buildings(), indent=2), encoding="utf-8")
        if peak_population <= initial_population:
            raise RuntimeError("Starter settlement did not attract immigrants")
    finally:
        env.close()


if __name__ == "__main__":
    main()
