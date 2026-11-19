"""Verify the composed food macro preserves previews and builds every component."""

import argparse
from julius_gym import JuliusEnv
from julius_gym.planner import decision_context, execute, fingerprint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=4000)
    try:
        observation, info = env.reset()
        before = fingerprint(env, observation)
        context, candidates = decision_context(env, observation, info["mission"], 0, 3000)
        assert fingerprint(env, observation) == before
        candidate = candidates["establish_wheat_supply"]
        assert len(candidate.actions) <= 128
        for kind in (5, 10, 11, 26, 27, 30, 35, 55):
            assert any(a[0] == kind for a in candidate.actions), f"Missing food component {kind}"
        observation, result, terminated, truncated = execute(env, candidate, observation, 3000)
        assert result["status"] == "completed" and not terminated and not truncated
        for _ in range(1600):
            observation, _, terminated, truncated, _ = env.step(0)
            assert not terminated and not truncated
        types = {b["type"] for b in env.get_buildings()}
        assert {100, 71, 70}.issubset(types)
        assert int(observation["population_total"].item()) > 0
        print(f"Composed food macro passed: {len(candidate.actions)} actions; population={observation['population_total'].item()}.")
    finally:
        env.close()


if __name__ == "__main__":
    main()
