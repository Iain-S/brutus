"""Check forecast rollback and equality to an actual charged continuation."""

import argparse
from julius_gym import JuliusEnv
from julius_gym.planner import decision_context, execute_cycle, fingerprint, forecast_state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=3000)
    try:
        observation, info = env.reset()
        before = fingerprint(env, observation)
        before_buildings = env.get_buildings()
        context, candidates = decision_context(env, observation, info["mission"], 0, 3000, forecast_ticks=1600)
        assert fingerprint(env, observation) == before
        assert env.get_buildings() == before_buildings
        assert all(c["forecast"]["ticks"] == 1600 for c in context["candidates"])
        candidate = candidates["establish_wheat_supply"]
        observation, result, terminated, truncated = execute_cycle(env, candidate, observation, 3000, 1600)
        assert not terminated and not truncated
        actual = forecast_state(env, observation, len(result["steps"]), result["status"])
        assert candidate.preview["forecast"] == actual, (candidate.preview["forecast"], actual)
        assert actual["population"] > 0
        before = fingerprint(env, observation)
        _, candidates = decision_context(env, observation, info["mission"], 1, 1400, forecast_ticks=8000)
        assert fingerprint(env, observation) == before
        assert all(c.preview["forecast"]["ticks"] <= 1400 for c in candidates.values())
        assert candidates["wait"].preview["forecast"]["status"] == "truncated"
    finally:
        env.close()
    print("Forecast rollback, actual outcome equality and episode-budget bounds passed.")


if __name__ == "__main__":
    main()
