"""Native compound controls, not model-selected gameplay or a strategy benchmark.

Run with explicit --data-dir and --lib-path. Keep durable previews, saves,
diagnostics and raw action traces for subsequent independent replay_run.py.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from julius_gym import JuliusEnv
from julius_gym.compound import ShortPlan, native_diagnostics, preview_short_plan
from julius_gym.planner import fingerprint, forecast_state
from julius_gym.run_artifacts import DEFAULT_RUNS, RunArtifacts


def main():
    if not __debug__:
        raise RuntimeError("Native evidence verification requires assertions; run without -O")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--lib-path", required=True, type=Path)
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    args = parser.parse_args()
    data, library, root = args.data_dir.resolve(), args.lib_path.resolve(), args.runs_dir.resolve()
    package = Path(__file__).resolve().parent / "julius_gym"
    sources = {path.name: path.read_bytes() for path in
               (Path(__file__).resolve(), package / "compound.py", package / "planner.py", package / "env.py")}
    source_hashes = {name: hashlib.sha256(content).hexdigest() for name, content in sources.items()}
    library_hash = hashlib.sha256(library.read_bytes()).hexdigest()
    env = JuliusEnv(data_directory=str(data), lib_path=str(library), campaign_rank=3, max_ticks=4000)
    directories = []
    try:
        # Fixed engineering fixtures exercise changing availability and nested
        # native snapshots. They are never offered as a model's winning sequence.
        for names in (("expand_housing", "establish_water_supply_district_0"),
                      ("establish_wheat_supply", "add_school_district_0"),
                      ("expand_housing", "missing_successor")):
            observation, info = env.reset()
            assert all(np_value.item() == env.get_observation()[key].item()
                       for key, np_value in observation.items()), "Native observation wrapper mismatch"
            initial = fingerprint(env, observation)
            diagnostics = native_diagnostics(env)
            plan = ShortPlan(initial, names)
            preview = preview_short_plan(env, plan, observation, info["mission"], 4000, 800)
            assert fingerprint(env, observation) == initial, "Compound changed base fingerprint"
            assert fingerprint(env, env.get_observation()) == initial, "Compound changed native scalars"
            assert native_diagnostics(env) == diagnostics, "Compound changed base diagnostics"
            assert preview["equal_time"], "Native control durations differ"
            if names[-1] == "missing_successor":
                assert preview["plan"]["status"] == "invalid_successor"
                assert not preview["plan"]["valid"]
                assert preview["plan"]["ticks"] == 800
            else:
                assert preview["plan"]["status"] == "completed", preview["plan"]["status"]
                assert preview["plan"]["valid"]
                assert preview["plan"]["ticks"] == 1600

            # Deliver each predicted branch by replaying its raw actions from
            # reset with NO candidate regeneration or forecast calls.
            for branch_name in ("plan", "control"):
                branch = preview[branch_name]
                # The plan continuation MUST begin at the restored base. Reset
                # here would conceal corruption of hidden native state. Its
                # archive is also replayed in a fresh process by replay_run.py.
                if branch_name == "control":
                    observation, info = env.reset()
                artifacts = RunArtifacts("compound-control", root, configuration={
                    "max_ticks": 4000, "fixture": names, "branch": branch_name,
                    "model_proposed": False, "strategic_evaluation": False})
                artifacts.ready = True
                artifacts.metadata["mission"] = info["mission"]
                artifacts.metadata["source_sha256"] = source_hashes
                artifacts.metadata["library_sha256"] = library_hash
                summary = None
                try:
                    source_directory = artifacts.directory / "source"
                    source_directory.mkdir()
                    for name, content in sources.items():
                        (source_directory / name).write_bytes(content)
                    (artifacts.directory / "preview.json").write_text(
                        json.dumps(preview, indent=2), encoding="utf-8")
                    stage_ends = {}
                    stage_diagnostics = {}
                    stage_observations = {}
                    for stage in branch["stages"]:
                        if "after" in stage:
                            stage_ends[stage["after"]["ticks"]] = stage["after"]
                            stage_diagnostics[stage["after"]["ticks"]] = stage["diagnostics"]
                            stage_observations[stage["after"]["ticks"]] = stage["after_observation"]
                    with artifacts.log.open("w", encoding="utf-8") as log:
                        for tick, expected in enumerate(branch["steps"], 1):
                            observation, reward, terminated, truncated, result = env.step_at(*expected["action"])
                            actual = {"action": expected["action"], "reward": reward,
                                      "terminated": terminated, "truncated": truncated, **result}
                            log.write(json.dumps(actual) + "\n")
                            assert actual["message"] == expected["message"], f"Message at {tick}"
                            assert abs(reward - expected["reward"]) <= 1e-6, f"Reward at {tick}"
                            assert not terminated and not truncated, f"Unexpected end at {tick}"
                            if tick in stage_ends:
                                assert forecast_state(env, observation, tick, "completed") == stage_ends[tick]
                                assert native_diagnostics(env) == stage_diagnostics[tick]
                                assert {k: int(v.item()) for k, v in observation.items()} == stage_observations[tick]
                    assert native_diagnostics(env) == branch["diagnostics"], "Six-endpoint replay mismatch"
                    assert {k: int(v.item()) for k, v in observation.items()} == branch["observation"]
                    assert forecast_state(env, observation, branch["ticks"], branch["status"]) == branch["forecast"]
                    summary = {"verified": True, "population": int(observation["population_total"].item()),
                               "ticks": branch["ticks"], "six_diagnostics_verified": True,
                               "forecast": branch["forecast"], "fixture": names, "branch": branch_name,
                               "model_proposed": False, "won": env.get_victory_state() == 1}
                finally:
                    artifacts.finish(env, summary, sys.exc_info()[1])
                directories.append(str(artifacts.directory))
    finally:
        env.close()
    print(json.dumps({"compound_controls_verified": True, "runs": directories}, indent=2))


if __name__ == "__main__":
    main()
