# Bounded Model-Proposed Compound Evaluation

> Continue inline in the existing authorized branch, tests first, fresh source
> review before inference, source-only commits. Preserve staged models and all
> previous failed evidence. The user delegated execution through a reviewable result.

**Goal:** Test whether the installed instruct model can propose, inspect and
execute legal two-step plans using the verified native preview foundation.

**Spec:** `docs/PLANNER_TODO.md`, Bounded Model Evaluation.

**Architecture:** Add a separate experimental runner; preserve the existing live
planner command. Three API calls per decision: choose a current first macro;
choose a second macro from its actual simulated successor menu; choose among
the compound forecast, the same model-chosen first macro followed by waiting,
and waiting alone. Every option lasts 1600 native ticks (two 800-tick cycles).
Use the same native initial state for every branch. Validate every model answer
against its exact request and regenerate every live successor action.

The sequential proposal protocol avoids guessing future district/building names.
All legal menu candidates remain visible/selectable; no human shortlist, forced
action, weighted score or build order. The single-step control shares the model's
root choice and is not an independently optimized one-step policy. This is a
feasibility experiment, not a causal planning-depth benchmark.

## Scope and interfaces

- `compound.py`: expose `successor_context(...)` which simulates a fresh current
  candidate for one cycle, generates a successor decision context, and always
  restores. Expose `execute_short_plan(...)` using the same rollout as previews;
  retain partial live progress on failure and enforce initial freshness.
- `examples/compound_planner.py`: pure request/validation/comparison helpers and
  a bounded local transport with exact requests, raw bodies, telemetry, timing,
  context hashes and fail-closed audit writes. No retries or fallback decisions.
- `examples/run_compound_planner.py`: separate opt-in audited experiment runner,
  real saves/six diagnostics, source/library hashes, per-decision JSON including
  proposal, native previews, comparison, selection and actual execution checks.

## Gates and experiment bounds

1. Proposal/schema validity, native forecast reliability, delivered execution,
   and strategic improvement remain separate gates. Invalid answers/forecasts
   stop the experiment, preserving the failure and previous actual trace.
2. Require completed 1600-tick previews and identical wait controls. No unequal
   duration endpoint comparison or silently accepted partial plan.
3. Keep installed `qwen3:4b-instruct-2507-q4_K_M`, digest
   `0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`;
   sampling .7/.8/20/0, context 8192, output cap 256, per-call cap 170 seconds.
4. Initial experiment: at most four decisions (12 API calls), 6400 actual ticks,
   episode max 8000. No retries, repair, model installation or security changes.
5. Independently audit requests/facts/selections and strict replay final raw
   actions/all six diagnostics. Report actual goals/resources without a score.

## Tasks and review focus

- [x] RED/GREEN: unit tests for successor freshness/restoration (including errors),
  shared live rollout, partial failure retention and before/after diagnostics.
- [x] RED/GREEN: pure protocol tests for schema/state/provenance/tick/type checks,
  full legal menu retention, all four ratings, selection boundaries and no mutation.
  Transport tests cover raw-response retention, duplicate keys, token/headroom,
  deadline rejection, audit I/O errors, and no calls after rejection.
- [x] Runner validation: no fabricated/fallback execution, durable attempted
  inference and actual partial actions, shared rollout equality and native replay.
- [x] Fresh review and all unittest modules, native health and controls. Commit
  verified source separately from generated evidence and unrelated staged work.
- [x] Run bounded model experiment, audit and independently replay. Record outcomes
  and limits in results/TODO; stop at a reviewable result, with failures preserved.

Review priorities: future menu/state identity; double-charged or uncharged time;
terminal prefixes and unequal controls; audit writes permitting unaudited action;
stale/tampered final alternatives; evidence mislabelled as model reasoning;
live partial actions disappearing from replay logs on failure.

## Ledger

Preflight: existing compound preview controls and 19 unit tests are the baseline.
Existing branch/workspace authorization continues; no worktree switch. Root and
successor proposals use complete legal menus; final output is ID-only with native,
adapter-owned evidence. The proposed design uses three sequential calls to avoid
trusting invented future identifiers. This costs extra inference and conditions
the continuation on the selected root; it cannot establish global plan optimality.

Implementation ledger: tests fail first for missing live/discovery interfaces,
protocol/runner modules and action sinks, then pass. Fresh source review finds
four material gaps: prefix-to-menu provenance, socket-only deadlines/HTTP error
retention, in-flight/completion telemetry, and finalization after damaged audit.
Regression cases reproduce the gaps before corrections. The final protocol binds
all first-stage actions/scalars/six diagnostics to the successor actually shown
to the model and to both model-proposed IDs. Each transport runs in a killable
child process with a wall-clock deadline; HTTP headers/raw body are written by
that child, including error/partial responses. In-flight attempt intent is atomic
and durable before dispatch. Completion requires literal done=True, stop reason,
and 1..256 generated tokens, plus existing positive prompt count/headroom guards.
Finalization preserves primary failures, treats unreadable audit counts as
unknown, still attempts native save/diagnostics, and closes the environment.

All 182 unittest cases pass (40 compound-related). Real local-server tests verify
HTTP 500 capture and termination of a stalled body. Native forecast health and
all previous compound rollback controls pass. A separate orchestration control
with explicitly labelled fixture answers executes housing/water through the
complete new protocol and live revalidation, matching all stage/final native
state and six diagnostics at 1600 ticks/population 42. This uses zero model/API
calls and is NOT part of the model evaluation. Its archive is
`runs/tarraco/2026-11-22/20261122T101451.597426Z_compound-orchestration-control_d897f3dd/`.

Ruling: keep full diagnostic/action prefix proof in local archives, but put only
its scalar/forecast summary in the successor prompt; the existing compact menu
retains native food/water/housing/finance summaries. This preserves 8K headroom
without asking the model to quote raw diagnostic JSON. Equivalent action-trace
groups are explicit in final comparisons: choosing a compound label under a tie
does not demonstrate preference for construction depth. No review findings are
deferred, and the existing planner CLI remains unchanged.

## Completed Experiment

On source `03089798`, archive
`runs/tarraco/2026-11-22/20261122T101738.483176Z_compound-model_11fb32a7/`
records four accepted decisions, twelve accepted API calls, no retries/fallbacks,
6400 delivered ticks and exact per-stage/final forecast matches. Selections are
housing/water, gardens/market, gardens/water, then water/wait after rejecting the
model-proposed second water macro. End population/fountain coverage are 49/49,
treasury 7458, health 50, favor 50, with food/culture/prosperity/peace/tax zero.
No native win or strategic improvement is claimed.

Independent archive audit reconstructs all requests, native prefix proofs and
final comparisons, validates raw response provenance/strict telemetry, source
hashes, menu availability, charged trace, selected execution and final payloads.
Its code and JSON are retained inside the source run. Fresh-process strict replay
at `runs/tarraco/2026-11-22/20261122T103511.549786Z_replay_081a68e5/`
matches every message/reward and all six native diagnostic endpoints. All 182
unittest cases, native health and controls pass; pip check passes. Actual saves
and six diagnostics are retained; real-asset PNG capture remains manual/pending.

Calls use 2581..5866 input and 15..34 output tokens, 46.6..68.3 seconds each,
730.7 inference seconds total; whole native run takes 988.2 seconds. Wheat supply
is legal in all eight model proposal menus and cultural services in seven, but
neither is selected. The market is still a food-related choice. Native comparison
facts and selection/execution gates pass, while strategy competence remains
unproven. Fixed final menu order, unseeded sampling, one chosen root/continuation
and the same-root single control preclude a causal planning-depth claim. All
four decisions have distinct alternative action traces (no tie-selection evidence).
