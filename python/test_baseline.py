#!/usr/bin/env python3
"""Integration regression: paid, connected construction and real immigration."""

import argparse

from julius_gym import JuliusEnv
from julius_gym.baseline import ROAD, connected_roads, starter_plan
from test_snapshot_restore import observation_digest


def run(env):
    obs, info = env.reset()
    terrain, buildings, width, height = env.get_map_data()
    assert not terrain[height:, :].any() and not terrain[:, width:].any()
    actions = starter_plan(terrain, buildings, width, height, info["mission"]["entry"])
    start_months = int(obs["time_total_months"].item())
    start_population = int(obs["population_total"].item())
    history = []
    for tick in range(3000):
        action = actions[tick] if tick < len(actions) else (0, 0, 0)
        before = int(obs["finance_treasury"].item())
        obs, reward, terminated, truncated, result = env.step_at(*action)
        assert not terminated and not truncated
        if action[0]:
            assert result["message"].startswith("Built "), (action, result)
            assert int(obs["finance_treasury"].item()) < before
        history.append((observation_digest(env, obs), reward, result))
    assert int(obs["time_total_months"].item()) > start_months
    assert int(obs["population_total"].item()) > start_population
    terrain, _, width, height = env.get_map_data()
    roads = connected_roads(terrain, width, height, info["mission"]["entry"])
    assert all((x, y) in roads for kind, x, y in actions if kind == 6)
    road = next((x, y) for kind, x, y in actions if kind == 6)
    # Occupied construction must fail without charging for another road.
    before = int(obs["finance_treasury"].item())
    obs, _, _, _, result = env.step_at(6, *road)
    assert not result["message"].startswith("Built ")
    assert int(obs["finance_treasury"].item()) == before
    assert terrain[road[1], road[0]] & ROAD
    return history, int(obs["population_total"].item())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path,
                    campaign_rank=3, max_ticks=4000)
    try:
        first, population = run(env)
        second, _ = run(env)
        assert first == second, "Constructed settlement reset replay diverged"
        print(f"Paid construction, connected roads, and reset replay passed; population={population}.")
    finally:
        env.close()


if __name__ == "__main__":
    main()
