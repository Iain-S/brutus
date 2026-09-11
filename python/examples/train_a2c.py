#!/usr/bin/env python3
"""
A2C Agent Training Example

Advantage Actor-Critic is very memory efficient and trains faster than PPO.
Best choice for limited GPU memory (4GB).

Memory usage: ~500MB-1GB GPU RAM during training
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from stable_baselines3 import A2C
    from stable_baselines3.common.callbacks import BaseCallback, CallbackList, CheckpointCallback
    from stable_baselines3.common.monitor import Monitor
    from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
    import torch
except ImportError:
    print("Error: stable-baselines3 not installed. Run: pip install stable-baselines3[extra]")
    sys.exit(1)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from julius_gym.wrappers import make_efficient_env
from julius_gym.env import ActionType


def tensorboard_available():
    """Check if tensorboard is available"""
    try:
        import tensorboard
        return True
    except ImportError:
        return False


def make_env(data_dir, scenario, max_ticks, lib_path=None, log_dir=None, rank=0, restrict_actions=None):
    """Create a single environment (for vectorization)"""
    def _init():
        if log_dir and rank > 0:
            os.makedirs(log_dir, exist_ok=True)
            log_path = Path(log_dir) / f"worker_{rank}.log"
            log_file = open(log_path, "a", buffering=1)
            sys.stdout = log_file
            sys.stderr = log_file

        env = make_efficient_env(
            data_directory=data_dir,
            scenario_file=scenario,
            max_ticks=max_ticks,
            lib_path=lib_path,
            simplify=True,
            normalize=True,
            flatten=True,
            shape_rewards=True,
            population_year_reward=True,
            restrict_actions=restrict_actions,
        )
        return Monitor(env)
    return _init


class PopulationEndCallback(BaseCallback):
    """Log population at the end of each population-year episode."""

    def _on_step(self) -> bool:
        dones = self.locals.get("dones")
        infos = self.locals.get("infos")
        if dones is None or infos is None:
            return True

        values = []
        for done, info in zip(dones, infos):
            if done and isinstance(info, dict) and "population_end" in info:
                values.append(info["population_end"])

        if values:
            avg_value = sum(values) / len(values)
            self.logger.record("rollout/population_end", avg_value)

        return True


def main():
    start_cwd = Path.cwd()
    parser = argparse.ArgumentParser(description="Train A2C agent on Julius")
    parser.add_argument(
        "--data-dir",
        required=True,
        help="Path to Caesar III data directory",
    )
    parser.add_argument(
        "--lib-path",
        help="Path to libjulius_gym library (optional, auto-detected if not provided)",
    )
    parser.add_argument(
        "--scenario",
        help="Path to scenario file (optional)",
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=3000,
        help="Maximum ticks per episode (default: 3000)",
    )
    parser.add_argument(
        "--timesteps",
        type=int,
        default=300000,
        help="Total training timesteps (default: 300000)",
    )
    parser.add_argument(
        "--n-envs",
        type=int,
        default=4,
        help="Number of parallel environments (default: 4)",
    )
    parser.add_argument(
        "--model-path",
        default="models/julius_a2c",
        help="Path to save model (default: models/julius_a2c)",
    )
    parser.add_argument(
        "--load",
        help="Load existing model from path",
    )
    parser.add_argument(
        "--no-gpu",
        action="store_true",
        help="Force CPU training",
    )
    parser.add_argument(
        "--building-only",
        action="store_true",
        help="Restrict actions to building and clear-land actions",
    )
    args = parser.parse_args()

    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_model_path = Path(args.model_path)
    if not base_model_path.is_absolute():
        base_model_path = (start_cwd / base_model_path).resolve()
    run_dir = base_model_path.parent / f"{base_model_path.stem}_{run_stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_model_path = run_dir / base_model_path.name

    # Check GPU availability
    device = "cpu" if args.no_gpu or not torch.cuda.is_available() else "cuda"
    print(f"Using device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    # Create vectorized environments for parallel training
    print(f"\nCreating {args.n_envs} parallel Julius environments...")
    print(f"  Data directory: {args.data_dir}")
    print(f"  Max ticks per episode: {args.max_ticks}")

    restrict_actions = None
    if args.building_only:
        restrict_actions = [
            ActionType.BUILD_HOUSING,
            ActionType.BUILD_ROAD,
            ActionType.BUILD_PLAZA,
            ActionType.BUILD_GARDEN,
            ActionType.BUILD_STATUE,
            ActionType.BUILD_PREFECTURE,
            ActionType.BUILD_ENGINEERS_POST,
            ActionType.BUILD_DOCTOR,
            ActionType.BUILD_HOSPITAL,
            ActionType.BUILD_BATHHOUSE,
            ActionType.BUILD_BARBER,
            ActionType.BUILD_SCHOOL,
            ActionType.BUILD_ACADEMY,
            ActionType.BUILD_LIBRARY,
            ActionType.BUILD_THEATER,
            ActionType.BUILD_AMPHITHEATER,
            ActionType.BUILD_COLOSSEUM,
            ActionType.BUILD_HIPPODROME,
            ActionType.BUILD_TEMPLE_SMALL,
            ActionType.BUILD_TEMPLE_LARGE,
            ActionType.BUILD_ORACLE,
            ActionType.BUILD_MARKET,
            ActionType.BUILD_GRANARY,
            ActionType.BUILD_WAREHOUSE,
            ActionType.BUILD_FOUNTAIN,
            ActionType.BUILD_WELL,
            ActionType.BUILD_FORUM,
            ActionType.BUILD_SENATE,
            ActionType.BUILD_GOVERNORS_VILLA,
            ActionType.BUILD_GOVERNORS_PALACE,
            ActionType.BUILD_WHEAT_FARM,
            ActionType.BUILD_VEGETABLE_FARM,
            ActionType.BUILD_FRUIT_FARM,
            ActionType.BUILD_OLIVE_FARM,
            ActionType.BUILD_VINES_FARM,
            ActionType.BUILD_PIG_FARM,
            ActionType.BUILD_CLAY_PIT,
            ActionType.BUILD_TIMBER_YARD,
            ActionType.BUILD_IRON_MINE,
            ActionType.BUILD_MARBLE_QUARRY,
            ActionType.BUILD_WINE_WORKSHOP,
            ActionType.BUILD_OIL_WORKSHOP,
            ActionType.BUILD_WEAPONS_WORKSHOP,
            ActionType.BUILD_FURNITURE_WORKSHOP,
            ActionType.BUILD_POTTERY_WORKSHOP,
            ActionType.BUILD_ACTOR_COLONY,
            ActionType.BUILD_GLADIATOR_SCHOOL,
            ActionType.BUILD_LION_HOUSE,
            ActionType.BUILD_CHARIOT_MAKER,
            ActionType.CLEAR_LAND,
        ]

    # Use SubprocVecEnv to leverage multiple CPU cores
    env = SubprocVecEnv([
        make_env(
            args.data_dir,
            args.scenario,
            args.max_ticks,
            args.lib_path,
            log_dir=str(run_dir / "worker_logs"),
            rank=i,
            restrict_actions=restrict_actions,
        )
        for i in range(args.n_envs)
    ])

    print(f"Environments created!")
    print(f"  Number of parallel envs: {args.n_envs}")
    print(f"  Observation space: {env.observation_space}")
    print(f"  Action space: {env.action_space}")
    print(f"  Run output directory: {run_dir}")

    if args.load:
        # Load existing model
        print(f"\nLoading model from {args.load}...")
        model = A2C.load(args.load, env=env, device=device)
        print("Model loaded!")
    else:
        # Create new model with memory-efficient hyperparameters
        print("\nCreating A2C model with memory-efficient settings...")
        model = A2C(
            "MlpPolicy",
            env,
            learning_rate=7e-4,
            n_steps=5,  # Very small for memory efficiency
            gamma=0.99,
            gae_lambda=1.0,
            ent_coef=0.01,
            vf_coef=0.25,
            max_grad_norm=0.5,
            rms_prop_eps=1e-5,
            use_rms_prop=True,
            policy_kwargs=dict(
                net_arch=dict(pi=[128, 128], vf=[128, 128]),  # Small network
            ),
            verbose=1,
            device=device,
            # tensorboard_log=f"./tensorboard/{Path(args.model_path).name}/",  # Disabled - requires tensorboard package
        )

        print(f"\nModel architecture:")
        print(f"  Policy network: [128, 128]")
        print(f"  Value network: [128, 128]")
        print(f"  N-steps: 5")
        print(f"  Parallel environments: {args.n_envs}")
        print(f"  Estimated GPU memory: ~500MB-1GB")
        print(f"\nA2C is very memory efficient and trains quickly!")
        print(f"It's the best choice for 4GB GPU constraints.")

        # Create callbacks
        checkpoint_callback = CheckpointCallback(
            save_freq=10000 // args.n_envs,  # Adjust for parallel envs
            save_path=str(run_dir / "checkpoints"),
            name_prefix="a2c_checkpoint",
        )
        population_callback = PopulationEndCallback()
        callbacks = CallbackList([checkpoint_callback, population_callback])

        # Train model
        print(f"\nTraining for {args.timesteps:,} timesteps...")
        print("Press Ctrl+C to stop training and save model\n")

        try:
            model.learn(
                total_timesteps=args.timesteps,
                callback=callbacks,
                progress_bar=False,  # Requires tqdm/rich: pip install stable-baselines3[extra]
            )
        except KeyboardInterrupt:
            print("\n\nTraining interrupted by user.")

        # Save model
        print(f"\nSaving model to {run_model_path}...")
        model.save(str(run_model_path))
        print("Model saved!")

    # Evaluate model
    print("\n" + "=" * 60)
    print("Evaluating trained model...")
    print("=" * 60)

    n_eval_episodes = 3
    terminated = False
    truncated = False

    print(f"Starting evaluation with {n_eval_episodes} episodes")
    print("Note: Creating fresh environment for each episode to avoid reset issues\n")

    for episode in range(n_eval_episodes):
        # Create a fresh environment for each episode to avoid segfault on reset
        print(f"Creating fresh environment for episode {episode + 1}")
        eval_env = make_efficient_env(
            data_directory=args.data_dir,
            scenario_file=args.scenario,
            max_ticks=args.max_ticks,
            lib_path=args.lib_path,
            simplify=True,
            normalize=True,
            flatten=True,
            shape_rewards=True,
            population_year_reward=True,
        )
        eval_env = Monitor(eval_env)

        obs, info = eval_env.reset()
        done = False
        episode_reward = 0
        step_count = 0

        print(f"\nEpisode {episode + 1}/{n_eval_episodes}")

        while not done and step_count < args.max_ticks:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = eval_env.step(action)

            episode_reward += reward
            step_count += 1
            done = terminated or truncated

            if step_count % 500 == 0:
                print(f"  Step {step_count}: reward={reward:.3f}, total={episode_reward:.3f}")

        print(f"\n  Episode finished!")
        print(f"    Steps: {step_count}")
        print(f"    Total reward: {float(episode_reward):.3f}")
        print(f"    Terminated: {terminated}, Truncated: {truncated}")

        # Render city map from the last evaluation episode
        if episode == n_eval_episodes - 1:
            print("\n" + "=" * 60)
            print("Rendering final city map...")
            print("=" * 60)
            try:
                # Get the underlying JuliusEnv from the wrapped environment
                base_env = eval_env
                while hasattr(base_env, 'env'):
                    base_env = base_env.env

                # Render and save the city map
                map_filename = str(run_dir / f"{base_model_path.stem}_final_city.png")
                base_env.render(mode="save", output_file=map_filename)
                print(f"City map saved to: {map_filename}")
            except Exception as e:
                print(f"Warning: Could not render city map: {e}")
                import traceback
                traceback.print_exc()

        # Close this episode's environment before creating the next one
        eval_env.close()

    env.close()

    print("\n" + "=" * 60)
    print("Training complete!")
    if not args.load:
        print(f"Model saved to: {run_model_path}")
    try:
        if 'map_filename' in locals():
            print(f"City map saved to: {map_filename}")
    except:
        pass
    print("=" * 60)


if __name__ == "__main__":
    main()
