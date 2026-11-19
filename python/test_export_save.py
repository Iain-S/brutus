"""Persistent save export after truncation must not advance simulation."""

import argparse
from pathlib import Path
import tempfile

from julius_gym import JuliusEnv
from julius_gym.run_artifacts import DEFAULT_RUNS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--lib-path", required=True)
    args = parser.parse_args()
    DEFAULT_RUNS.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=DEFAULT_RUNS) as directory:
        save = Path(directory).resolve() / "final.sav"
        env = JuliusEnv(data_directory=args.data_dir, lib_path=args.lib_path, campaign_rank=3, max_ticks=1)
        try:
            env.reset()
            _, _, _, truncated, _ = env.step(0)
            assert truncated
            token = env.get_state_token()
            env.export_save(save)
            assert env.get_state_token() == token, "Export advanced simulation state"
            assert save.stat().st_size > 1000, "No substantive saved-game data"
        finally:
            env.close()
        assert save.exists(), "Export was deleted with environment"
    print("Persistent post-truncation save export passed.")


if __name__ == "__main__":
    main()
