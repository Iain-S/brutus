#!/usr/bin/env python3
"""Integration test for masked road-then-housing placement actions."""

import argparse
import os
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Test road/housing curriculum")
    parser.add_argument("--data-dir", type=Path, default=os.environ.get("JULIUS_DATA_DIR"))
    parser.add_argument("--scenario", type=Path, default=os.environ.get("JULIUS_SCENARIO"))
    parser.add_argument("--lib-path", type=Path, default=os.environ.get("JULIUS_LIB_PATH"))
    return parser.parse_args()


def require_path(name, value):
    path = Path(value) if value else None
    if path is None or not path.exists():
        raise ValueError(f"{name} is required and must exist")
    return path


def main():
    args = parse_args()
    try:
        data_dir = require_path("--data-dir", args.data_dir)
        scenario = require_path("--scenario", args.scenario)
        lib_path = require_path("--lib-path", args.lib_path)
    except ValueError as error:
        print(f"Skipping: {error}.")
        return 0

    from julius_gym.wrappers import make_road_housing_curriculum_env

    env = make_road_housing_curriculum_env(
        data_directory=str(data_dir),
        scenario_file=str(scenario),
        lib_path=str(lib_path),
        candidate_count=4,
        target_houses=1,
    )
    try:
        observation, _ = env.reset()
        assert observation.shape == (10,)
        initial_mask = env.action_masks()
        assert initial_mask[1]
        assert not initial_mask[1 + 4]

        _, road_reward, terminated, truncated, _ = env.step(1)
        assert road_reward == 0.1
        assert not terminated and not truncated
        assert env.action_masks()[1 + 4]

        _, house_reward, terminated, truncated, info = env.step(1 + 4)
        assert house_reward == 6.0
        assert terminated and not truncated
        assert info["placement_goal_reached"] is True
    finally:
        env.close()

    print("Road/housing curriculum test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
