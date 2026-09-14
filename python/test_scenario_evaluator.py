#!/usr/bin/env python3
"""Data-gated repeatability test for fixed-scenario evaluation."""

import argparse

from julius_gym.env import JuliusEnv
from julius_gym.evaluation import evaluate_action_plan


def evaluate_once(args):
    env = JuliusEnv(
        data_directory=args.data_dir,
        scenario_file=args.scenario,
        lib_path=args.lib_path,
        max_ticks=args.max_ticks,
    )
    try:
        return evaluate_action_plan(env, [], args.max_ticks)
    finally:
        env.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--lib-path", required=True)
    parser.add_argument("--max-ticks", type=int, default=3)
    args = parser.parse_args()

    first = evaluate_once(args)
    second = evaluate_once(args)
    assert first == second, (first, second)
    assert first["outcome"] == "truncated"
    assert first["ticks"] == args.max_ticks
    print("Scenario evaluator repeatability test passed.")


if __name__ == "__main__":
    main()
