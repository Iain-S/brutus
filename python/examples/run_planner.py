#!/usr/bin/env python3
"""Run a bounded Tarraco planner via a JSON stdin/stdout model command."""

import argparse
import json
from pathlib import Path
import sys
import subprocess
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from julius_gym import JuliusEnv
from julius_gym.planner import command_choice, decision_context, execute, rule_choice, validate_choice


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--lib-path", required=True, type=Path)
    parser.add_argument("--model-command", help='JSON argv array, e.g. ["python", "absolute/path/to/model_adapter.py"]')
    parser.add_argument("--max-ticks", type=int, default=3000)
    parser.add_argument("--max-decisions", type=int, default=10)
    parser.add_argument("--model-timeout", type=int, default=60, help="Seconds per local command attempt (1..300)")
    parser.add_argument("--log", type=Path, default=Path("runs/planner.jsonl"))
    args = parser.parse_args()
    command = json.loads(args.model_command) if args.model_command else None
    if command is not None and (not isinstance(command, list) or not command
                                or not all(isinstance(s, str) and s for s in command)):
        parser.error("--model-command must be a nonempty JSON argv array")
    if args.max_ticks < 1 or args.max_decisions < 1:
        parser.error("Budgets must be positive")
    if not 1 <= args.model_timeout <= 300:
        parser.error("--model-timeout must be from 1 to 300 seconds")
    log_path = args.log.resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # The engine changes cwd. Resolve user paths before constructing the env.
    data, library = str(args.data_dir.resolve()), str(args.lib_path.resolve())
    if command:
        # Executable lookup is normal PATH lookup; file arguments should be absolute.
        original_cwd = str(Path.cwd())
    env = JuliusEnv(data_directory=data, lib_path=library, campaign_rank=3, max_ticks=args.max_ticks)
    try:
        observation, info = env.reset()
        mission = info["mission"]
        if mission["is_tutorial"] or mission["combat_events"] or mission["gladiator_revolt"]:
            raise RuntimeError("Planner requires a non-tutorial peaceful mission")
        ticks, calls, last = 0, 0, None
        terminated = truncated = False
        with log_path.open("w", encoding="utf-8") as log:
            for decision in range(args.max_decisions):
                context, candidates = decision_context(env, observation, mission, decision,
                                                      args.max_ticks - ticks, last)
                errors = []
                for attempt in range(2):
                    try:
                        if command:
                            # Run adapters from the launch directory, not the game data directory.
                            current_cwd = os.getcwd()
                            try:
                                os.chdir(original_cwd)
                                calls += 1
                                choice = command_choice(command, {**context, "validation_errors": errors}, args.model_timeout)
                            finally:
                                os.chdir(current_cwd)
                        else:
                            choice = rule_choice(context, candidates)
                        candidate = validate_choice(choice, context, candidates)
                        break
                    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
                        errors.append(type(error).__name__ + ": " + str(error)[:300])
                else:
                    candidate = candidates["wait"]
                    choice = {"decision_id": decision, "candidate_id": "wait", "reason": "Validation failure fallback"}
                observation, last, terminated, truncated = execute(env, candidate, observation, args.max_ticks - ticks)
                ticks += len(last["steps"])
                log.write(json.dumps({"context": context, "choice": choice, "errors": errors, "result": last}) + "\n")
                log.flush()
                if terminated or truncated or ticks >= args.max_ticks:
                    break
        print(json.dumps({"mode": "command" if command else "rule-smoke", "ticks": ticks,
                          "model_calls": calls, "population": int(observation["population_total"].item()),
                          "terminated": terminated, "truncated": truncated,
                          "stop_reason": "episode_end" if terminated or truncated else "decision_budget",
                          "log": str(log_path)}, indent=2))
    finally:
        env.close()


if __name__ == "__main__":
    main()
