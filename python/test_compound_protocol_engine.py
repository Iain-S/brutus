"""Native orchestration control with fixture answers; no model/API calls."""

import argparse
from pathlib import Path
import sys

from julius_gym import JuliusEnv
from julius_gym.run_artifacts import DEFAULT_RUNS, RunArtifacts

sys.path.insert(0, str(Path(__file__).resolve().parent / "examples"))
from run_compound_planner import run_decision
from compound_planner import write_json


class FixtureAnswers:
    def call(self, stage, body, validate):
        # Known engineering fixture from the native checkpoint, never a model
        # response or an evaluation of human-prescribed gameplay strategy.
        ids = {"first": "expand_housing", "successor": "establish_water_supply_district_0",
               "selection": "compound"}
        value = {"decision_id": 0, "candidate_id": ids[stage]}
        if stage != "selection":
            value["reason"] = "engineering fixture, not model output"
        validate(value)
        return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--lib-path", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    args = parser.parse_args()
    data, library = args.data_dir.resolve(), args.lib_path.resolve()
    artifacts = RunArtifacts("compound-orchestration-control", args.runs_dir, configuration={
        "max_ticks": 8000, "model_proposed": False, "api_calls": 0, "engineering_fixture": True})
    env = JuliusEnv(data_directory=str(data), lib_path=str(library), campaign_rank=3, max_ticks=8000)
    summary = None
    try:
        observation, info = env.reset()
        artifacts.ready = True
        artifacts.metadata["mission"] = info["mission"]
        with artifacts.log.open("w", encoding="utf-8") as log:
            def on_step(step):
                import json
                log.write(json.dumps(step) + "\n")
                log.flush()
            actual = run_decision(env, observation, info["mission"], 0, 8000,
                                  artifacts.directory / "decision-00", FixtureAnswers(), on_step)
        if actual["ticks"] != 1600 or actual["observation"]["population_total"] != 42:
            raise RuntimeError("Native orchestration fixture changed")
        summary = {"population": 42, "ticks": 1600, "execution_verified": True,
                   "api_calls": 0, "model_proposed": False, "won": False}
        write_json(artifacts.directory / "control-summary.json", summary)
    finally:
        try:
            artifacts.finish(env, summary, sys.exc_info()[1])
        finally:
            env.close()


if __name__ == "__main__":
    main()
