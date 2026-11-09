"""Exercise transient wind and terminal-state rollback through native test hooks."""

import argparse
import ctypes

from julius_gym import JuliusEnv


class VictoryState(ctypes.Structure):
    _fields_ = [("state", ctypes.c_int), ("force_win", ctypes.c_int)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=20000)
    try:
        env.reset()
        env.lib.city_victory_force_win.argtypes = []
        env.lib.city_victory_force_win.restype = None
        with env.snapshot() as snapshot:
            env.lib.city_victory_force_win()
            _, _, terminated, _, _ = env.step(0)
            assert terminated and env.get_victory_state() == 1
            snapshot.restore()
            assert env.get_victory_state() == 0, "Speculative victory leaked after restore"
            _, _, terminated, _, _ = env.step(0)
            assert not terminated, "Speculative force-win flag leaked after restore"

        # Inject only the transient result for a defeat; campaign rules stay unchanged.
        restore_victory = env.lib.city_victory_restore_state
        restore_victory.argtypes = [ctypes.POINTER(VictoryState)]
        restore_victory.restype = None
        with env.snapshot() as snapshot:
            restore_victory(ctypes.byref(VictoryState(-1, 0)))
            assert env.get_victory_state() == -1
            snapshot.restore()
            assert env.get_victory_state() == 0, "Speculative defeat leaked after restore"

        env.lib.city_victory_reset.argtypes = []
        env.lib.city_victory_reset.restype = None
        env.lib.city_victory_force_win()
        with env.snapshot() as snapshot:
            env.lib.city_victory_reset()
            snapshot.restore()
            _, _, terminated, _, _ = env.step(0)
            assert terminated and env.get_victory_state() == 1, "Snapshot lost a preexisting force-win flag"
        env.reset()

        wind = env.lib.building_maintenance_fire_direction
        wind.argtypes = []
        wind.restype = ctypes.c_int
        before = wind()
        with env.snapshot() as snapshot:
            for _ in range(9600):
                _, _, terminated, truncated, _ = env.step(0)
                assert not terminated and not truncated
            assert wind() != before, "Test did not exercise an annual wind change"
            snapshot.restore()
            assert wind() == before, "Speculative annual wind leaked after restore"

        restore_wind = env.lib.building_maintenance_restore_fire_direction
        restore_wind.argtypes = [ctypes.c_int]
        restore_wind.restype = None
        restore_wind(3)
        env.reset()
        assert wind() == 0, "Previous episode's wind leaked into a fresh mission"
    finally:
        env.close()
    print("Victory, defeat, force-win flag and year-boundary wind rollback passed.")


if __name__ == "__main__":
    main()
