"""Food diagnostics must be read-only, restorable and available at episode end."""

import argparse
import ctypes
from julius_gym import JuliusEnv
from julius_gym.planner import decision_context, execute, fingerprint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=1800)
    try:
        observation, info = env.reset()
        assert env.get_food_supply()["buildings"] == []
        _, candidates = decision_context(env, observation, info["mission"], 0, 1800)
        observation, result, _, _ = execute(env, candidates["establish_wheat_supply"], observation, 1800)
        assert result["status"] == "completed"
        for _ in range(100):
            observation, _, _, _, _ = env.step(0)
        before = fingerprint(env, observation)
        buildings = env.get_buildings()
        supply = env.get_food_supply()
        assert supply["schema_version"] == 1 and supply["units_per_load"] == 100
        assert supply["food_order"] == ["wheat", "vegetables", "fruit", "meat"]
        assert {b["kind"] for b in supply["buildings"]} == {"farm", "granary", "market"}
        for row in supply["buildings"]:
            assert row["workers_required"] > 0
            assert row["road_access"] == 1
            if row["kind"] == "farm":
                assert 0 <= row["progress_points"] <= row["progress_max"] == 200
            else:
                assert len(row["food_units"]) == 4 and min(row["food_units"]) >= 0
        assert env.get_food_supply() == supply
        assert fingerprint(env, observation) == before and env.get_buildings() == buildings
        tiny = ctypes.create_string_buffer(b"X" * 16, 16)
        assert env.lib.julius_env_get_food_supply(env.env_handle, tiny, 4) == -1
        assert tiny.raw[4:] == b"X" * 12
        assert env.lib.julius_env_get_food_supply(None, tiny, 4) == -1
        with env.snapshot() as snapshot:
            for _ in range(500):
                env.step(0)
            snapshot.restore()
            assert env.get_food_supply() == supply
        while True:
            _, _, terminated, truncated, _ = env.step(0)
            if terminated or truncated:
                break
        assert env.get_food_supply()["buildings"]
        env.reset()
        assert env.get_food_supply()["buildings"] == []
    finally:
        env.close()
    print("Food query units, read-only state, bounds, snapshot, terminal and reset checks passed.")


if __name__ == "__main__":
    main()
