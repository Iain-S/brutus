# Candidate-only pilot continuation

Continue the existing three-decision/nine-call candidate-only pilot after an
orchestration error, preserving its original limits and failed record.

## Verified starting point

The original run is
`runs/tarraco/2026-11-27/20261127T095922.321453Z_candidate-only-pilot_74f24163/`.
All three decision-5 calls choose `house_farm_workers_17`; exact delivery adds
800 ticks. Population reaches 114, farm workers 10, food coverage 57, fountain
coverage 50 and treasury 6263. The run remains ERROR: a request dictionary
overwrites the game-data path before the next independent replay subprocess.
No model output failure or native forecast mismatch caused that stop.

Preserve the original runner and artifacts. The copied continuation uses
`request_data` instead of rebinding the native data path. A regression check
fails on the original binding and passes on the copy; all eleven offline
checks pass. Fresh read-only review finds no material issues.

Full primitive replay verifies the saved 16800-tick city, delivered monthly
checkpoint and six diagnostics:
`runs/tarraco/2026-11-27/20261127T101007.612375Z_candidate-only-outcome-replay_833dfdd8/`.
All 45 next-state roots independently replay through 4800 ticks/six checkpoints:
`runs/tarraco/2026-11-27/20261127T101053.712627Z_candidate-replay-recheck_8ec44024/case-00`.
Pinned inventory SHA-256:
`d6f738703dce5e43fc1f72ff130645db7d8d3ccde407fb574a6d4df40fd44f06`.

## Frozen continuation protocol

- Start from the pinned, independently verified partial source, at 16800 ticks.
- At most two more decisions, IDs 6 and 7, six calls and 1600 delivered ticks.
  Combined with the first run: at most three decisions, nine calls, 2400 ticks.
- Retain the candidate-only typed schema and host-bound freshness checks.
  All roots, field meanings, horizons, prompts and model limits remain fixed.
- Require original/reversed/original agreement and exact repeat request bytes
  before each 800-tick delivery. No retries, majority vote or response repair.
- Stop on unsafe context telemetry, invalid output, disagreement or failed
  replay; preserve partial progress without promoting the failed experiment.
- Recheck the full actual trace and all six final diagnostics independently.

Ignored helpers: `runs/candidate_only_continuation.py`,
`runs/check_candidate_only_continuation.py`,
`runs/audit_candidate_only_continuation.py`,
`runs/replay_candidate_only_outcome.py` and preparation/mock helpers.
Mock archive:
`runs/candidate-only-continuation-validation/20261127T101636.250979Z/`.
Independent audit verifies all 3105 native cells per table, the full 45-root
schema and host bindings. Mock usage is synthetic and does not establish real
45-root context headroom; actual response telemetry must pass unchanged limits.

## Outcome

Pending the bounded continuation. This is an experimental runner, not a
production dependency migration or evidence of a campaign win.
