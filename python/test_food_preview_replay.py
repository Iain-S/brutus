"""Detailed food state must replay from reset without speculative branches."""

import argparse
from julius_gym import JuliusEnv
from julius_gym.planner import decision_context, execute_cycle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=7000)
    try:
        observation, info = env.reset()
        actions, expected, ticks = [], [], 0
        names = ["expand_housing", "establish_wheat_supply", "expand_housing", "expand_housing",
                 "add_market_district_0", "wait", "wait", "wait"]
        for decision, name in enumerate(names):
            _, candidates = decision_context(env, observation, info["mission"], decision, 7000 - ticks,
                                             forecast_ticks=1600)
            observation, result, terminated, truncated = execute_cycle(env, candidates[name], observation,
                                                                      7000 - ticks, 800)
            assert not terminated and not truncated and result["status"] == "completed"
            actions.extend(step["action"] for step in result["steps"])
            ticks += len(result["steps"])
            expected.append(env.get_food_supply())
        assert any(row["kind"] == "farm" and row["workers"] > 0 for row in expected[-1]["buildings"])
        env.reset()
        for index, action in enumerate(actions, 1):
            _, _, terminated, truncated, _ = env.step_at(*action)
            assert not terminated and not truncated
            if index % 800 == 0:
                assert env.get_food_supply() == expected[index // 800 - 1], f"Food replay diverged at tick {index}"
    finally:
        env.close()
    print("Detailed food inventories, progress and figure references replayed without previews.")


if __name__ == "__main__":
    main()
