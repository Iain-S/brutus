"""Housing must remain buildable beyond the formerly self-colliding ninth block."""

import argparse
from julius_gym import JuliusEnv
from julius_gym.baseline import exclude_hazard, starter_plan
from julius_gym.env import ActionType as A
from julius_gym.planner import Candidate, execute_cycle, fingerprint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=8000)
    try:
        observation, info = env.reset()
        ticks = 0
        for index in range(9):
            terrain, buildings, width, height = env.get_map_data()
            terrain = exclude_hazard(terrain, info["mission"]["earthquake"], 14)
            actions = starter_plan(terrain, buildings, width, height, info["mission"]["entry"])
            roads = {(x, y) for kind, x, y in actions if kind == A.BUILD_ROAD}
            occupied = {(x, y) for kind, x, y in actions if kind != A.BUILD_ROAD}
            assert not roads & occupied, f"Housing block {index + 1} crosses its own access road"
            candidate = Candidate("expand_housing", actions, fingerprint(env, observation), {})
            observation, result, terminated, truncated = execute_cycle(env, candidate, observation, 8000 - ticks, 800)
            assert result["status"] == "completed" and not terminated and not truncated, result
            ticks += len(result["steps"])
        assert int(observation["buildings_housing"].item()) > 64
    finally:
        env.close()
    print("Nine paid housing blocks passed without access-road self-collisions.")


if __name__ == "__main__":
    main()
