"""Replay recorded actions with/without speculative forecasts on one environment.

Historical final payloads are intentionally not an oracle: this control compares
two fresh resets, never calls a model, and preserves the original action log.
"""

import argparse
import ctypes
import json
import math
from pathlib import Path
import sys

from julius_gym import JuliusEnv
from julius_gym.planner import decision_context
from julius_gym.run_artifacts import RunArtifacts


MAX_TICKS = 12800
FORECAST_TICKS = 1600


def read_initial_cursor(env):
    """Require the repair's native getter; never silently skip GREEN coverage."""
    query = env.lib.city_labor_water_allocation_cursor
    query.argtypes = []
    query.restype = ctypes.c_int
    return query()


def capture(env, observation):
    return {"buildings": env.get_buildings(), "food": env.get_food_supply(),
            "imperial": env.get_imperial_state(), "water": env.get_water_supply(),
            "housing": env.get_housing_state(), "finance": env.get_finance_state(),
            "population": int(observation["population_total"].item()),
            "victory": env.get_victory_state()}


def difference_paths(expected, actual, path="", limit=16):
    """Bound diagnostic output only; the pass/fail comparison is always full."""
    if expected == actual:
        return []
    if isinstance(expected, dict) and isinstance(actual, dict):
        paths = []
        for key in sorted(expected.keys() | actual.keys()):
            child = f"{path}.{key}" if path else str(key)
            if key not in expected or key not in actual:
                paths.append(child + " (missing key)")
            else:
                paths.extend(difference_paths(expected[key], actual[key], child, limit - len(paths)))
            if len(paths) >= limit:
                break
        return paths
    if isinstance(expected, list) and isinstance(actual, list):
        paths = [path + ".length"] if len(expected) != len(actual) else []
        for index, (left, right) in enumerate(zip(expected, actual)):
            if len(paths) >= limit:
                break
            paths.extend(difference_paths(left, right, f"{path}[{index}]", limit - len(paths)))
        return paths
    return [f"{path}: {expected!r} != {actual!r}"]


def replay(env, blocks, source, with_previews, baseline=None):
    artifacts = RunArtifacts("preview-replay-control", configuration={
        "max_ticks": MAX_TICKS, "source_run": str(source),
        "with_previews": with_previews, "forecast_ticks": FORECAST_TICKS if with_previews else 0})
    summary = None
    try:
        observation, info = env.reset()
        artifacts.ready = True
        mission = info["mission"]
        artifacts.metadata["mission"] = mission
        initial_cursor = read_initial_cursor(env)
        artifacts.metadata["initial_water_allocation_cursor"] = initial_cursor
        artifacts.metadata["water_cursor_hook_available"] = True
        assert initial_cursor == 1, f"Reset water allocation cursor is {initial_cursor}, expected 1"
        ticks = 0
        with artifacts.log.open("w", encoding="utf-8") as log:
            for decision_id, block in enumerate(blocks):
                if with_previews:
                    # Generate every normal candidate/forecast, then discard all
                    # choices. Only the original recorded actions go live.
                    cursor_before = read_initial_cursor(env)
                    decision_context(env, observation, mission, decision_id,
                                     MAX_TICKS - ticks, forecast_ticks=FORECAST_TICKS)
                    cursor_after = read_initial_cursor(env)
                    assert cursor_after == cursor_before, (
                        f"Forecast changed water allocation cursor at block {decision_id}: "
                        f"{cursor_before} != {cursor_after}")
                for expected in block:
                    observation, reward, terminated, truncated, info = env.step_at(*expected["action"])
                    ticks += 1
                    actual = {"tick": ticks, "decision_id": decision_id,
                              "action": expected["action"], "reward": reward,
                              "terminated": terminated, "truncated": truncated, **info}
                    log.write(json.dumps(actual) + "\n")
                    assert (expected["message"] == actual["message"]
                            and math.isfinite(expected["reward"]) and math.isfinite(reward)
                            and abs(reward - expected["reward"]) <= 1e-6), (
                                f"Step diverged at tick {ticks}: expected {expected}, got {actual}")
                    assert not (terminated or truncated) or ticks == MAX_TICKS, (
                        f"Episode ended early at tick {ticks}: {actual}")
                log.flush()
                print(json.dumps({"with_previews": with_previews,
                                  "completed_blocks": decision_id + 1, "ticks": ticks}), flush=True)
        final = capture(env, observation)
        summary = {"ticks": ticks, "population": final["population"], "won": final["victory"] == 1,
                   "source_run": str(source), "with_previews": with_previews,
                   "blocks": len(blocks), "all_recorded_steps_matched": True,
                   "initial_water_allocation_cursor": initial_cursor,
                   "comparison_status": "baseline_only" if baseline is None else "pending"}
        assert ticks == MAX_TICKS, ticks
        if baseline is not None:
            # Water first for the suspected regression; every payload is still
            # compared, including the scalar population and victory state.
            mismatched = [key for key in ("water", "buildings", "food", "imperial", "housing",
                                          "finance", "population", "victory")
                          if baseline["final"][key] != final[key]]
            cursor_error = None
            if initial_cursor != 1 or baseline["initial_cursor"] != 1:
                cursor_error = {"expected_reset_value": 1, "without_previews": baseline["initial_cursor"],
                                "with_previews": initial_cursor}
            comparison = {"baseline_run": str(baseline["directory"]),
                          "mismatched_payloads": mismatched, "reset_cursor_error": cursor_error,
                          "difference_paths": {key: difference_paths(baseline["final"][key], final[key])
                                               for key in mismatched}}
            (artifacts.directory / "comparison.json").write_text(
                json.dumps(comparison, indent=2), encoding="utf-8")
            summary["mismatched_payloads"] = mismatched
            summary["comparison_status"] = "failed" if mismatched or cursor_error else "matched"
            print(json.dumps(comparison, indent=2), flush=True)
            assert not mismatched and cursor_error is None, (
                f"Preview replay diverged: payloads={mismatched}, reset_cursor_error={cursor_error}; "
                f"diagnostics: {artifacts.directory / 'comparison.json'}")
        return {"final": final, "initial_cursor": initial_cursor, "directory": artifacts.directory}
    finally:
        artifacts.finish(env, summary, sys.exc_info()[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--lib-path", type=Path, required=True)
    parser.add_argument("--source-run", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_run.resolve()
    manifest = json.loads((source / "run.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in Path(manifest["actions"]).read_text(encoding="utf-8").splitlines()]
    if manifest.get("status") != "finished" or manifest["configuration"]["max_ticks"] != MAX_TICKS:
        parser.error("Source must be a finished 12,800-tick recorded run")
    if len(rows) != 16 or any(not row.get("result", {}).get("steps") for row in rows):
        parser.error("Source must contain 16 nonempty recorded action blocks")
    blocks = [row["result"]["steps"] for row in rows]
    if sum(map(len, blocks)) != MAX_TICKS:
        parser.error("Recorded action blocks must total exactly 12,800 ticks")
    env = JuliusEnv(data_directory=str(args.data_dir.resolve()), lib_path=str(args.lib_path.resolve()),
                    campaign_rank=manifest["mission"]["campaign_rank"], max_ticks=MAX_TICKS)
    try:
        baseline = replay(env, blocks, source, with_previews=False)
        replay(env, blocks, source, with_previews=True, baseline=baseline)
        print("All steps, six final diagnostics, population, victory and reset cursors match.", flush=True)
    finally:
        env.close()


if __name__ == "__main__":
    main()
