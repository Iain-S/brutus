#!/usr/bin/env python3
"""Replay two expanded baseline runs and verify a working food production chain."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--lib-path", type=Path, required=True)
    args = parser.parse_args()
    runner = Path(__file__).parent / "examples" / "run_baseline.py"
    traces = []
    with tempfile.TemporaryDirectory(prefix="food-baseline-", dir=Path.cwd()) as directory:
        for run in range(2):
            log = Path(directory) / f"run-{run}.jsonl"
            result = subprocess.run(
                [sys.executable, str(runner.resolve()), "--data-dir", str(args.data_dir.resolve()),
                 "--lib-path", str(args.lib_path.resolve()), "--food", "--blocks", "5",
                 "--max-ticks", "24000", "--log", str(log.resolve())],
                capture_output=True, text=True,
            )
            if result.returncode:
                raise AssertionError(result.stdout + result.stderr)
            records = [json.loads(line) for line in log.read_text().splitlines()]
            traces.append(records)
            actions = {record["action"][0] for record in records[1:]}
            assert {26, 27, 35, 55}.issubset(actions), "Missing food-chain construction"
            assert records[-1]["population"] > 49, "No expansion beyond starter population"
            assert records[-1]["food_stocks"] > 0, "No stored food from production chain"
            assert records[-1]["farms"] > 0, "Farm did not survive the longer run"
            assert records[-1]["residents_with_food"] > 0, "Stored food never reached houses"
            buildings = json.loads(log.with_suffix(".buildings.json").read_text())
            assert any(b["type"] == 71 and b["workers"] > 0 for b in buildings), "Granary is unstaffed"
            assert any(b["type"] == 70 and b["workers"] > 0 for b in buildings), "Markets are unstaffed"
            assert all(0 <= b["food"] and 0 <= b["population"] for b in buildings)
            assert all(not record["terminated"] for record in records[1:])
        assert traces[0] == traces[1], "Expanded baseline traces diverged across fresh runs"
    print("Bridge, staffed storage, household food delivery, farm survival and replay passed.")


if __name__ == "__main__":
    main()
