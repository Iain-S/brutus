# Model-Directed Forecast Lookup Plan

> Execute inline with tests first, explicit source-only commits and a fresh
> final review. Preserve staged models, native rules and historical failures.

**Goal:** Test the user-requested two-stage interface after the failed one-pass
evidence gate. The model requests alternatives; the adapter returns native
facts; the model makes an independently checked final choice.

## Design

Add an experimental pure helper module `python/examples/ollama_planner_lookup.py`,
not a new runner/CLI flag. Reuse the committed one-pass formatter, inference
guards and strict comparison validator. Existing commands/defaults stay intact.
This tests model-directed retrieval rather than weakening checks, dropping
failing fields, choosing a human shortlist or changing model/game balance.

Stage 1 retains the original complete compact context and every legal ID/value.
Its response is exactly `decision_id`, `candidate_ids`: two distinct legal
IDs, or one if only wait exists. No facts are quoted or final action executed.
The request does not prescribe an alternative, scoring function or build order.

Stage 2 preserves the original compact non-candidate context (including goals,
state, services and recent outcomes) and replaces the large candidate table
and baseline encoding with a lookup result for the MODEL'S requested IDs.
The result contains all twenty fully materialized forecast fields for those
IDs and actual wait, macro durations/outlay, and explicitly named comparison
facts including the native blocked-house difference versus wait. Known zeros
are explicit zeros; unknowns remain null. Input arithmetic is adapter-produced
native data, not a repaired model answer. Record a canonical full-context hash,
decision and query IDs for provenance. Copy all data; do not mutate context.

The output retains the existing verified-comparison schema, narrowed only to
the model's own query IDs. Validate the lookup's full contents and context
hash against the original context, exact queried-ID membership, every quoted
field/type and final selected ID. Use the original raw-context validator,
not the returned lookup as an oracle. No new free-text rationale or tolerated
errors. The legacy three-key choice is produced only after full acceptance.

This stage intentionally supplies explicit facts before generation. It is a
different I/O task, not proof the model independently reconstructs packed
forecasts, understands facts, or selects good actions. Self-shortlisting may
miss better alternatives; stage 1 can request any original legal candidate.

## Tasks

- [x] RED: add `python/test_planner_lookup.py` for full stage-1 facts/IDs/options,
  exact query schema/types/counts/distinctness/current identity, single wait,
  materialized values/types/unknowns/outlay/provenance, no input mutation,
  stage-2 retained common context and model-only ID restriction, strict quote
  validation and stale/tampered lookup rejection. Observe missing API failures.
- [x] GREEN: implement pure helpers `lookup_request_body`, `validate_lookup`,
  `materialize_lookup`, `lookup_choice_request_body`, `verified_lookup_choice`
  and `context_fingerprint`. No network/session/runner code. Document the
  experimental interface and limits, run all focused planner/replay tests,
  compare old requests against `346402c2`, review and commit/push source only.
- [ ] On committed helpers, run four frozen transactions (two repetitions on
  decisions 5 and 7 of verified `planner-local_03ba650f`). Each has at most two
  API calls and no retry, fallback or game action. Same pinned instruct model,
  8K context, 256 output tokens and existing sampling per call. Each API call
  retains the 170-second cap; a transaction has a 290-second total deadline,
  including both stages and validation. Record per-call and cumulative time,
  all request/response/error data, queried IDs and exact native lookup facts.
- [ ] Independently audit both stages, all scalar values/types and provenance,
  exact membership/quotes, token/headroom checks and cumulative deadlines.
  Frozen feasibility passes only with four accepted complete transactions.
  Do not run stage 2 after invalid query/inference, silently retry, repair
  quotes, omit failures or reinterpret the old failed gate. Record results,
  limitations and the next checkpoint; review and commit/push documentation.

## Budgets And Artifacts

Two stages necessarily change call count/total allowance: up to eight API calls
for four transactions, versus four in the failed one-pass probe. Per-call
inference settings are unchanged; 290 seconds is a NEW total transaction
budget, not the old 170-second one-call budget. No claim of equal compute or
isolated representation causality. A future live adapter would need explicit
multi-call telemetry and an outer timeout exceeding its total deadline; the
runner's current `model_calls` counts command invocations, not API calls.
Do not silently integrate this helper as a live command.

Use `runs/planner-input-probes/YYYY-MM-DD/<UTC>_fact-lookup_<uuid8>/` with exact
source/protocol/hash snapshots, frozen contexts, lookups, both stages' requests,
raw responses and audit. Set `native_execution: false`, `executed_choices: 0`.
Reference the old verified trace/save/replay rather than creating or copying a
native save. All generated outputs, weights, assets and local configuration
stay out of commits; preserve unrelated staged model artifacts.

The user requested this next checkpoint and delegated continued investigation.
Continue the existing authorized branch/workspace and integration route without
a worktree switch or repeated design/integration questions. Choices above are
engineering decisions, not user-prescribed gameplay. No live trial follows
automatically: a passing frozen interface is not campaign competence or a win.

## Source Verification

Observed RED for the missing helper module before implementation. Ten new
test cases now pass with 85 focused planner and seven replay tests. Tests
cover all-ID queries, exact schema/types/counts/order, full 20-field native
lookup normalization, unknowns, single wait, provenance, no mutation, retained
common context, raw-context quote validation and stale/tampered/unqueried-ID
rejection. Fresh source review found no issues and independently passed the
same focused suites.

The original adapter source is unchanged. Eighteen occupied-state request
cases (both states, three forecast formats, all three existing profiles) are
byte-identical to `346402c2`. No native, runner, CLI or default-profile change
is introduced. The four frozen transaction gate remains pending; passing
helper tests is not evidence that the local model can use the new interface.
