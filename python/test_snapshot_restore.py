#!/usr/bin/env python3
"""Regression test for deterministic reset and JuliusEnv snapshots.

Requires licensed Caesar III data and a scenario. Supply paths with command-line
arguments or JULIUS_DATA_DIR, JULIUS_LIB_PATH, and JULIUS_SCENARIO.
"""

import argparse
import hashlib
import os
import struct
import sys
from pathlib import Path

import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Test Julius Gym reset and snapshots")
    parser.add_argument("--data-dir", type=Path, default=os.environ.get("JULIUS_DATA_DIR"))
    parser.add_argument("--lib-path", type=Path, default=os.environ.get("JULIUS_LIB_PATH"))
    parser.add_argument("--scenario", type=Path, default=os.environ.get("JULIUS_SCENARIO"))
    parser.add_argument("--steps", type=int, default=12)
    return parser.parse_args()


def require_path(name, value):
    path = Path(value) if value else None
    if path is None or not path.exists():
        raise ValueError(f"{name} is required and must exist")
    return path


def observation_digest(env, observation):
    """Hash exported state, including map layers, without relying on dict order."""
    digest = hashlib.sha256()
    for key in sorted(observation):
        digest.update(key.encode("utf-8"))
        digest.update(np.asarray(observation[key], dtype=np.int32).tobytes())
    terrain, buildings, width, height = env.get_map_data()
    digest.update(struct.pack("<ii", width, height))
    digest.update(terrain.tobytes())
    digest.update(buildings.tobytes())
    return digest.hexdigest()


def run_trace(env, steps):
    observation, _ = env.reset()
    trace = [("reset", observation_digest(env, observation))]
    for _ in range(steps):
        observation, reward, terminated, truncated, info = env.step(0)
        trace.append(
            (
                "step",
                observation_digest(env, observation),
                float(reward),
                bool(terminated),
                bool(truncated),
                info.get("message", ""),
            )
        )
        if terminated or truncated:
            break
    return trace


def run_suffix(env, steps):
    trace = []
    for _ in range(steps):
        observation, reward, terminated, truncated, info = env.step(0)
        trace.append(
            (
                observation_digest(env, observation),
                float(reward),
                bool(terminated),
                bool(truncated),
                info.get("message", ""),
            )
        )
        if terminated or truncated:
            break
    return trace


def main():
    args = parse_args()
    try:
        data_dir = require_path("--data-dir", args.data_dir)
        lib_path = require_path("--lib-path", args.lib_path)
        scenario = require_path("--scenario", args.scenario)
    except ValueError as error:
        print(f"Skipping: {error}.")
        return 0

    from julius_gym import JuliusEnv

    env = JuliusEnv(
        data_directory=str(data_dir),
        scenario_file=str(scenario),
        max_ticks=1000,
        lib_path=str(lib_path),
    )
    try:
        first_trace = run_trace(env, args.steps)
        second_trace = run_trace(env, args.steps)
        if first_trace != second_trace:
            raise AssertionError("Reset is not deterministic within one environment")

        env.reset()
        run_suffix(env, 4)
        with env.snapshot() as snapshot:
            expected = run_suffix(env, args.steps)
            snapshot.restore()
            actual = run_suffix(env, args.steps)
        if expected != actual:
            raise AssertionError("Restored snapshot diverged from uninterrupted episode")
    finally:
        env.close()

    print("Reset and snapshot determinism test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
