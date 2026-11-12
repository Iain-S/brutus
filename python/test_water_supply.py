"""Asset-backed paid water construction, staffing and snapshot/replay control."""

import argparse
import ctypes
import json
import sys

from julius_gym import JuliusEnv
from julius_gym.env import ActionType as A
from julius_gym.planner import Candidate, decision_context, execute, fingerprint, food_supply_plan, preview_candidate
from julius_gym.baseline import NOT_CLEAR, building_plan, exclude_hazard, starter_plan
from julius_gym.run_artifacts import RunArtifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    artifacts = RunArtifacts("water-capability", configuration={"max_ticks": 16000})
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=16000)
    try:
        observation, info = env.reset()
        artifacts.ready = True
        artifacts.metadata["mission"] = info["mission"]
        initial = env.get_water_supply()
        query = env.lib.julius_env_get_water_supply
        tiny = ctypes.create_string_buffer(b"X" * 16)
        assert query(env.env_handle, tiny, 4) == -1 and tiny.raw[4:5] == b"X"
        assert query(env.env_handle, None, 20) == -1
        assert query(None, tiny, len(tiny)) == -1
        assert A.SEND_LAVISH_GIFT == 58 and A.BUILD_RESERVOIR == 59 and A.COUNT == 61
        before = fingerprint(env, observation)
        assert env.get_water_supply() == initial and fingerprint(env, observation) == before
        ticks = 0
        with artifacts.log.open("w", encoding="utf-8") as log:
            def apply(name, actions):
                nonlocal observation, ticks
                candidate = Candidate(name, actions, fingerprint(env, observation), {})
                observation, result, terminated, truncated = execute(env, candidate, observation, 16000 - ticks)
                for step in result["steps"]:
                    log.write(json.dumps(step) + "\n")
                ticks += len(result["steps"])
                assert result["status"] == "completed" and not terminated and not truncated, result
            terrain, buildings, width, height = env.get_map_data()
            terrain = exclude_hazard(terrain, info["mission"]["earthquake"], 14)
            apply("housing", starter_plan(terrain, buildings, width, height, info["mission"]["entry"]))
            apply("food", food_supply_plan(env, info["mission"], 14))
            terrain, buildings, width, height = env.get_map_data()
            terrain = exclude_hazard(terrain, info["mission"]["earthquake"], 14)
            home = next((b["x"], b["y"]) for b in env.get_buildings() if b["level"] >= 0)
            apply("religion", building_plan(terrain, buildings, width, height, info["mission"]["entry"],
                                            A.BUILD_TEMPLE_SMALL, 2, anchor=home))
            apply("immigration", [(A.NONE, 0, 0)] * 800)
            from julius_gym.water import water_plan
            home = next((b["x"], b["y"]) for b in env.get_buildings() if b["level"] >= 0)
            terrain, buildings, width, height = env.get_map_data()
            isolated = next((x, y) for y in range(1, height - 2) for x in range(1, width - 3)
                            if abs(x - home[0]) + abs(y - home[1]) > 20
                            and all(not buildings[y, tx] and not terrain[y, tx] & (NOT_CLEAR & ~0x11)
                                    for tx in (x, x + 1)))
            x, y = isolated
            phase = []
            for tx in (x, x + 1):
                if terrain[y, tx] & 0x11:
                    phase.append((A.CLEAR_LAND, tx, y))
                phase.append((A.BUILD_AQUEDUCT, tx, y))
            apply("isolated_dry_aqueduct", phase)
            water = env.get_water_supply()
            assert water["aqueducts"] and not any(tile["water"] for tile in water["aqueducts"]), water
            before = env.get_water_supply()
            actions = water_plan(env, info["mission"], home)
            assert env.get_water_supply() == before
            context, candidates = decision_context(env, observation, info["mission"], 0, 16000 - ticks)
            assert any(name.startswith("establish_water_supply_") for name in candidates)
            assert "water_supply" in context and env.get_water_supply() == before
            candidate = Candidate("water", actions, fingerprint(env, observation), {})
            result, _, _ = preview_candidate(env, candidate, observation, 16000 - ticks, forecast_ticks=800)
            assert result["status"] == "completed" and env.get_water_supply() == before
            apply("water", actions)
            apply("activation", [(A.NONE, 0, 0)] * 1600)
            water = env.get_water_supply()
            assert any(b["kind"] == "reservoir" and b["water_access"] for b in water["buildings"]), water
            assert any(b["kind"] == "fountain" and b["water_access"] and b["workers"] for b in water["buildings"]), water
            assert any(b["population"] and b["fountain"] for b in env.get_buildings())
            from julius_gym.water import AQUEDUCT, aqueduct_route, reservoir_sites
            source = next((b["x"], b["y"]) for b in water["buildings"]
                          if b["kind"] == "reservoir" and b["water_access"])
            terrain, buildings, width, height = env.get_map_data()
            terrain = exclude_hazard(terrain, info["mission"]["earthquake"], 14)
            for target in reservoir_sites(terrain, buildings, width, height, source, near_water=False):
                x, y = target
                if (terrain[y - 1:y + 4, x - 1:x + 4] & 4).any():
                    continue
                try:
                    route = aqueduct_route(terrain, buildings, width, height, source, target)
                except RuntimeError:
                    continue
                if len(route) < 64:
                    break
            else:
                raise AssertionError("No dry relay test site")
            x, y = target
            clearing = [(A.CLEAR_LAND, tx, ty) for ty in range(y, y + 3) for tx in range(x, x + 3)
                        if terrain[ty, tx] & 0x11]
            apply("dry_relay", clearing + [(A.BUILD_RESERVOIR, x, y)])
            apply("observe_dry", [(A.NONE, 0, 0)] * 800)
            relay = next(b for b in env.get_water_supply()["buildings"] if (b["x"], b["y"]) == target)
            assert not relay["near_water"] and not relay["water_access"], relay
            phase = []
            for tx, ty in route:
                if terrain[ty, tx] & 0x11:
                    phase.append((A.CLEAR_LAND, tx, ty))
                if not terrain[ty, tx] & AQUEDUCT:
                    phase.append((A.BUILD_AQUEDUCT, tx, ty))
            apply("aqueduct", phase)
            apply("observe_wet", [(A.NONE, 0, 0)] * 800)
            water = env.get_water_supply()
            relay = next(b for b in water["buildings"] if (b["x"], b["y"]) == target)
            assert not relay["near_water"] and relay["water_access"], relay
            assert any(tile["water"] for tile in water["aqueducts"]), water
            for action in ((A.BUILD_RESERVOIR, *source), (A.BUILD_RESERVOIR, width - 2, height - 2),
                           (A.BUILD_AQUEDUCT, *next((x, y) for y in range(height) for x in range(width)
                                                  if terrain[y, x] & 4))):
                candidate = Candidate("invalid_water", [action], fingerprint(env, observation), {})
                observation, result, _, _ = execute(env, candidate, observation, 16000 - ticks)
                ticks += len(result["steps"])
                for step in result["steps"]:
                    log.write(json.dumps(step) + "\n")
                assert result["status"] == "failed", result
            # Supply is not the only native prerequisite: the starter's nearby
            # safety/industry buildings also depress house desirability.
            terrain, buildings, width, height = env.get_map_data()
            hx, hy = home
            garden_sites = [(x, y) for y in range(max(1, hy - 4), min(height - 1, hy + 5))
                            for x in range(max(1, hx - 4), min(width - 1, hx + 5))
                            if not buildings[y, x] and not terrain[y, x] & (NOT_CLEAR & ~0x11)]
            garden_sites.sort(key=lambda p: (abs(p[0] - hx) + abs(p[1] - hy), p))
            phase = []
            for x, y in garden_sites[:12]:
                if terrain[y, x] & 0x11:
                    phase.append((A.CLEAR_LAND, x, y))
                phase.append((A.BUILD_GARDEN, x, y))
            apply("fixture_desirability", phase)
            apply("evolution", [(A.NONE, 0, 0)] * 8000)
            assert max(b["level"] for b in env.get_buildings()) >= 4
        summary = {"ticks": ticks, "population": int(observation["population_total"].item()),
                   "won": False, "verified_water_access": True,
                   "max_house_level": max(b["level"] for b in env.get_buildings())}
        print(json.dumps(summary))
    finally:
        try:
            artifacts.finish(env, locals().get("summary"), sys.exc_info()[1])
        finally:
            env.close()


if __name__ == "__main__":
    main()
