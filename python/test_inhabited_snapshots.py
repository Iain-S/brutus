"""Snapshot replay must preserve inhabited-city service walkers and fire risk."""

import argparse
from julius_gym import JuliusEnv
from julius_gym.baseline import starter_plan
from julius_gym.planner import Candidate, decision_context, execute_cycle, fingerprint, proposals


def advance(env, ticks):
    samples = []
    for index in range(ticks):
        _, _, terminated, truncated, _ = env.step(0)
        assert not terminated and not truncated
        if index % 50 == 0:
            samples.append(env.get_buildings())
    return samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=6000)
    try:
        _, info = env.reset()
        for _ in range(3):
            for action in starter_plan(*env.get_map_data(), info["mission"]["entry"]):
                _, _, terminated, truncated, result = env.step_at(*action)
                assert result["message"].startswith("Built ") and not terminated and not truncated
        advance(env, 1200)
        assert any(b["population"] > 0 for b in env.get_buildings())
        with env.snapshot() as snapshot:
            expected = advance(env, 1000)
            snapshot.restore()
            actual = advance(env, 1000)
        assert expected == actual, "Inhabited-city snapshot changed walkers or maintenance state"
        traces = []
        for with_previews, forecast_ticks in ((False, 0), (True, 0), (True, 1600)):
            observation, info = env.reset()
            states = []
            ticks = 0
            for decision, name in enumerate(["connect_farmland"] + ["expand_housing"] * 7):
                if with_previews:
                    _, candidates = decision_context(env, observation, info["mission"], decision, 5000 - ticks,
                                                     forecast_ticks=forecast_ticks)
                    candidate = candidates[name]
                else:
                    make = dict(proposals(env, info["mission"], 14))[name]
                    candidate = Candidate(name, make(), fingerprint(env, observation), {})
                observation, result, terminated, truncated = execute_cycle(env, candidate, observation, 5000 - ticks, 400)
                assert result["status"] == "completed" and not terminated and not truncated
                ticks += len(result["steps"])
                states.append(env.get_buildings())
            traces.append(states)
        assert all(trace == traces[0] for trace in traces[1:]), "Candidate previews changed the inhabited city"
    finally:
        env.close()
    print("Inhabited-city snapshot replay passed.")


if __name__ == "__main__":
    main()
