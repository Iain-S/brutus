#!/usr/bin/env python3
"""Train MaskablePPO to build connected road-and-house pairs on one map."""

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from julius_gym.wrappers import make_road_housing_curriculum_env


def parse_args():
    parser = argparse.ArgumentParser(description="Train road/housing placement curriculum")
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--lib-path", required=True)
    parser.add_argument("--timesteps", type=int, default=5000)
    parser.add_argument("--candidate-count", type=int, default=8)
    parser.add_argument("--target-houses", type=int, default=3)
    parser.add_argument("--max-ticks", type=int, default=8)
    parser.add_argument("--eval-episodes", type=int, default=30)
    parser.add_argument("--model-path", type=Path, default=Path("models/road_housing/ppo"))
    return parser.parse_args()


def make_env(args):
    return make_road_housing_curriculum_env(
        data_directory=args.data_dir,
        scenario_file=args.scenario,
        lib_path=args.lib_path,
        max_ticks=args.max_ticks,
        candidate_count=args.candidate_count,
        target_houses=args.target_houses,
    )


def evaluate(model, args):
    successes = 0
    rewards = []
    for _ in range(args.eval_episodes):
        env = make_env(args)
        try:
            observation, _ = env.reset()
            total_reward = 0.0
            for _ in range(args.max_ticks):
                action, _ = model.predict(
                    observation, deterministic=True, action_masks=env.action_masks()
                )
                observation, reward, terminated, truncated, info = env.step(action)
                total_reward += reward
                if terminated or truncated:
                    successes += int(info.get("placement_goal_reached", False))
                    break
            rewards.append(total_reward)
        finally:
            env.close()
    return successes / args.eval_episodes, sum(rewards) / len(rewards)


def main():
    args = parse_args()
    start_cwd = Path.cwd()
    if not args.model_path.is_absolute():
        args.model_path = (start_cwd / args.model_path).resolve()
    env = make_env(args)
    try:
        model = MaskablePPO(
            "MlpPolicy",
            env,
            learning_rate=3e-4,
            n_steps=64,
            batch_size=64,
            n_epochs=4,
            gamma=0.95,
            ent_coef=0.01,
            policy_kwargs={"net_arch": {"pi": [64, 64], "vf": [64, 64]}},
            verbose=0,
            device="cpu",
        )
        model.learn(total_timesteps=args.timesteps, progress_bar=False)
        success_rate, mean_reward = evaluate(model, args)
        args.model_path.parent.mkdir(parents=True, exist_ok=True)
        model.save(args.model_path)
        print(f"Evaluation success rate: {success_rate:.1%}")
        print(f"Evaluation mean reward: {mean_reward:.3f}")
        if success_rate < 0.8:
            raise RuntimeError("Placement curriculum did not reach the 80% success threshold")
    finally:
        env.close()


if __name__ == "__main__":
    main()
