#!/usr/bin/env python3
"""Verify a campaign action log from reset without model calls or preview branches."""

import argparse
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from julius_gym import JuliusEnv
from julius_gym.run_artifacts import DEFAULT_RUNS, RunArtifacts


def recorded_steps(rows):
    for row in rows:
        if "result" in row:
            yield from row["result"]["steps"]
        elif "action" in row:
            yield row


def assert_step_matches(expected, actual, tick):
    if (expected["message"] != actual["message"]
            or not math.isfinite(expected["reward"]) or not math.isfinite(actual["reward"])
            or abs(actual["reward"] - expected["reward"]) > 1e-6):
        raise AssertionError(f"Replay diverged at tick {tick}: expected {expected}, got {actual}")


def verify_food_supply(env, path):
    if not path.exists():
        return False
    if env.get_food_supply() != json.loads(path.read_text(encoding="utf-8")):
        raise AssertionError("Final food supply diagnostics differ from recorded run")
    return True


def verify_imperial_state(env, path):
    if not path.exists():
        return False
    if env.get_imperial_state() != json.loads(path.read_text(encoding="utf-8")):
        raise AssertionError("Final imperial diagnostics differ from recorded run")
    return True


def verify_water_supply(env, path):
    if not path.exists():
        return False
    if env.get_water_supply() != json.loads(path.read_text(encoding="utf-8")):
        raise AssertionError("Final water supply diagnostics differ from recorded run")
    return True


def verify_housing_state(env, path):
    if not path.exists():
        return False
    if env.get_housing_state() != json.loads(path.read_text(encoding="utf-8")):
        raise AssertionError("Final housing diagnostics differ from recorded run")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--lib-path", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    args = parser.parse_args()
    source = args.run.resolve()
    manifest = json.loads((source / "run.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in Path(manifest["actions"]).read_text(encoding="utf-8").splitlines()]
    expected_buildings = json.loads((source / "final.buildings.json").read_text(encoding="utf-8"))
    steps = list(recorded_steps(rows))
    if not steps or manifest.get("status") != "finished":
        parser.error("Replay requires a finished run with recorded actions")
    artifacts = RunArtifacts("replay", args.runs_dir, configuration={
        "source_run": str(source), "max_ticks": manifest["configuration"]["max_ticks"]})
    env = JuliusEnv(data_directory=str(args.data_dir.resolve()), lib_path=str(args.lib_path.resolve()),
                    campaign_rank=manifest["mission"]["campaign_rank"],
                    max_ticks=manifest["configuration"]["max_ticks"])
    try:
        observation, info = env.reset()
        artifacts.ready = True
        artifacts.metadata["mission"] = info["mission"]
        with artifacts.log.open("w", encoding="utf-8") as log:
            for index, expected in enumerate(steps, 1):
                observation, reward, terminated, truncated, result = env.step_at(*expected["action"])
                actual = {"tick": index, "action": expected["action"], "reward": reward,
                          "terminated": terminated, "truncated": truncated, **result}
                log.write(json.dumps(actual) + "\n")
                assert_step_matches(expected, actual, index)
                if (terminated or truncated) and index != len(steps):
                    raise AssertionError("Replay ended before the recorded trace")
        if env.get_buildings() != expected_buildings:
            raise AssertionError("Final building diagnostics differ from recorded run")
        food_verified = verify_food_supply(env, source / "final.food_supply.json")
        imperial_verified = verify_imperial_state(env, source / "final.imperial.json")
        water_verified = verify_water_supply(env, source / "final.water_supply.json")
        housing_verified = verify_housing_state(env, source / "final.housing.json")
        population = int(observation["population_total"].item())
        if population != manifest["summary"]["population"]:
            raise AssertionError("Final population differs from recorded run")
        if env.get_victory_state() != manifest["victory_state"]:
            raise AssertionError("Final victory state differs from recorded run")
        summary = {"verified": True, "ticks": len(steps), "population": population,
                   "source_run": str(source), "won": env.get_victory_state() == 1,
                   "food_supply_verified": food_verified, "imperial_state_verified": imperial_verified,
                   "water_supply_verified": water_verified, "housing_state_verified": housing_verified}
        print(json.dumps(summary, indent=2))
    finally:
        error = sys.exc_info()[1]
        try:
            artifacts.finish(env, locals().get("summary"), error)
        finally:
            env.close()


if __name__ == "__main__":
    main()
