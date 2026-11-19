"""Culture candidates must build normally and preserve speculative state."""

import argparse
from julius_gym import JuliusEnv
from julius_gym.planner import decision_context, execute, fingerprint
from test_snapshot_restore import run_suffix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=6000)
    try:
        observation, info = env.reset()
        _, candidates = decision_context(env, observation, info["mission"], 0, 6000)
        observation, result, _, _ = execute(env, candidates["expand_housing"], observation, 6000)
        assert result["status"] == "completed"
        ticks = len(result["steps"])
        for _ in range(100):
            observation, _, _, _, _ = env.step(0)
            ticks += 1
        for decision, name in enumerate(("school", "library", "theater", "actor_colony"), 1):
            before = fingerprint(env, observation)
            _, candidates = decision_context(env, observation, info["mission"], decision, 6000 - ticks)
            assert fingerprint(env, observation) == before
            candidate = candidates[f"add_{name}_district_0"]
            assert len(candidate.actions) <= 128
            observation, result, terminated, truncated = execute(env, candidate, observation, 6000 - ticks)
            assert result["status"] == "completed" and not terminated and not truncated
            ticks += len(result["steps"])
        for _ in range(4800 - ticks):
            observation, _, terminated, truncated, _ = env.step(0)
            assert not terminated and not truncated
        records = env.get_buildings()
        assert {31, 36, 51, 53}.issubset({b["type"] for b in records})
        assert int(observation["buildings_education"].item()) == 2
        assert int(observation["buildings_entertainment"].item()) == 2
        assert int(observation["ratings_culture"].item()) > 0, "Culture buildings produced no observed rating progress"
        context, _ = decision_context(env, observation, info["mission"], 5, 1200)
        assert all(context["services"][name] == 1 for name in ("schools", "libraries", "theaters", "actor_colonies"))
        with env.snapshot() as snapshot:
            expected = run_suffix(env, 100)
            snapshot.restore()
            decision_context(env, observation, info["mission"], 6, 1200, forecast_ticks=800)
            actual = run_suffix(env, 100)
            assert actual == expected, "Culture previews changed the independent simulation suffix"
        print("Paid culture construction, preview rollback and rating progress passed:",
              int(observation["ratings_culture"].item()))
    finally:
        env.close()


if __name__ == "__main__":
    main()
