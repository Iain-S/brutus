#!/usr/bin/env python3
"""Evaluate a fixed Caesar III scenario using a short explicit action plan."""

import argparse
import json
from pathlib import Path

from julius_gym.env import ActionType, JuliusEnv
from julius_gym.evaluation import evaluate_action_plan


def parse_action(value):
    """Parse ``BUILD_ROAD@18,1`` into an action type and map coordinate."""
    try:
        name, coordinates = value.upper().split("@", maxsplit=1)
        x_text, y_text = coordinates.split(",", maxsplit=1)
        action = getattr(ActionType, name.removeprefix("ACTION_"))
        return action, int(x_text), int(y_text)
    except (AttributeError, ValueError) as exc:
        raise argparse.ArgumentTypeError(
            "actions must be ACTION_NAME@x,y, e.g. BUILD_ROAD@18,1"
        ) from exc


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--lib-path", required=True)
    parser.add_argument("--max-ticks", type=positive_int, default=5000)
    parser.add_argument(
        "--action", action="append", type=parse_action, default=[],
        help="Plan action: ACTION_NAME@x,y. May be repeated; remaining ticks wait.",
    )
    parser.add_argument("--json-out", type=Path, help="Optional report destination")
    return parser.parse_args()


def positive_int(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return value


def main():
    args = parse_args()
    output_path = args.json_out.resolve() if args.json_out else None
    env = JuliusEnv(
        data_directory=args.data_dir,
        scenario_file=args.scenario,
        lib_path=args.lib_path,
        max_ticks=args.max_ticks,
    )
    try:
        report = evaluate_action_plan(env, args.action, args.max_ticks)
    finally:
        env.close()
    report["scenario"] = Path(args.scenario).name
    print(json.dumps(report, indent=2, sort_keys=True))
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
