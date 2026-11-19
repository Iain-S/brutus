#!/usr/bin/env python3
"""Automated reset/step stability test for JuliusEnv."""

import argparse
import os
import sys
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="JuliusEnv reset/step stability test")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(os.environ.get("JULIUS_DATA_DIR", "")),
        help="Path to Caesar III data directory (or set JULIUS_DATA_DIR)",
    )
    parser.add_argument(
        "--lib-path",
        type=Path,
        default=Path(os.environ.get("JULIUS_LIB_PATH", "")),
        help="Path to libjulius_gym (or set JULIUS_LIB_PATH)",
    )
    parser.add_argument(
        "--scenario",
        type=Path,
        default=Path(os.environ.get("JULIUS_SCENARIO", "")),
        help="Optional scenario file (or set JULIUS_SCENARIO)",
    )
    parser.add_argument(
        "--resets",
        type=int,
        default=5,
        help="Number of resets to perform (default: 5)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=10,
        help="Number of steps per reset (default: 10)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        import julius_gym
    except ModuleNotFoundError as exc:
        print(f"Skipping: missing dependency ({exc}).")
        print("Install python requirements to run this test.")
        return 0

    if not args.data_dir or not args.data_dir.exists():
        print("Skipping: data directory not provided or does not exist.")
        print("Set --data-dir or JULIUS_DATA_DIR to run this test.")
        return 0

    if not args.lib_path or not args.lib_path.exists():
        print("Skipping: lib path not provided or does not exist.")
        print("Set --lib-path or JULIUS_LIB_PATH to run this test.")
        return 0

    scenario_path = None
    if args.scenario and args.scenario.exists():
        scenario_path = str(args.scenario)

    env = julius_gym.JuliusEnv(
        data_directory=str(args.data_dir),
        scenario_file=scenario_path,
        max_ticks=1000,
        lib_path=str(args.lib_path),
    )

    try:
        for reset_idx in range(args.resets):
            obs, info = env.reset()
            # Basic sanity check on observation keys
            required_keys = [
                "ratings_culture",
                "finance_treasury",
                "population_total",
                "labor_workers_employed",
                "resources_food_stocks",
                "time_year",
            ]
            for key in required_keys:
                if key not in obs:
                    raise RuntimeError(f"Missing observation key: {key}")

            done = False
            for step_idx in range(args.steps):
                obs, reward, terminated, truncated, info = env.step(0)
                done = terminated or truncated
                if done:
                    break

        print("Reset/step stability test passed.")
        return 0
    finally:
        env.close()


if __name__ == "__main__":
    sys.exit(main())
