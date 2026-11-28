"""Physical building aggregates must agree with engine records, not count buckets."""

import argparse
from julius_gym import JuliusEnv
from julius_gym.planner import decision_context, execute


def settle(env):
    for _ in range(100):
        observation, _, terminated, truncated, _ = env.step(0)
        assert not terminated and not truncated
    return observation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=3000)
    try:
        observation, info = env.reset()
        assert int(observation["buildings_total_buildings"].item()) == 0
        _, candidates = decision_context(env, observation, info["mission"], 0, 3000)
        observation, result, terminated, truncated = execute(env, candidates["establish_wheat_supply"], observation, 3000)
        assert result["status"] == "completed" and not terminated and not truncated
        assert int(observation["buildings_food_buildings"].item()) == 2, "Farm/granary aggregate is incorrect"
        observation = settle(env)
        for name in ("add_doctor_district_0", "add_temple_district_0"):
            _, candidates = decision_context(env, observation, info["mission"], 1, 2500)
            observation, result, terminated, truncated = execute(env, candidates[name], observation, 2500)
            assert result["status"] == "completed" and not terminated and not truncated
        observation = settle(env)
        records = env.get_buildings()
        assert int(observation["buildings_total_buildings"].item()) == len(records), "Total is not a physical record count"
        for key, types in {
            "food_buildings": {100, 101, 102, 103, 104, 105, 71},
            "industrial_buildings": {110, 111, 112, 113, 114},
            "health": {46, 47, 48, 49},
            "education": {51, 52, 53},
            "religious": set(range(60, 70)) | {98},
        }.items():
            assert int(observation["buildings_" + key].item()) == sum(b["type"] in types for b in records), key
        observation, _ = env.reset()
        assert int(observation["buildings_total_buildings"].item()) == 0
        assert int(observation["buildings_food_buildings"].item()) == 0
    finally:
        env.close()
    print("Physical building totals, food categories and reset isolation passed.")


if __name__ == "__main__":
    main()
