# Native Compound Previews Implementation Plan

> Execute inline with tests first and a fresh source review. The user delegated
> continuation through a reviewable result; retain the current workspace and
> preserve unrelated staged models. No live model promotion in this checkpoint.

**Goal:** Establish trustworthy two-step native forecasts before model evaluation.

**Architecture:** An additive `julius_gym.compound` module accepts one or two
candidate names bound to the initial native fingerprint. Resolve names through
`decision_context` in each successor state, then use `execute_cycle` to charge
construction and observation ticks. An outer snapshot encloses the entire plan
and an equal-time wait control; restore on every exit, including exceptions.

**Tech Stack:** Existing Python, unittest, Julius native snapshot/diagnostics API.

**Spec:** `docs/PLANNER_TODO.md`, Native Compound Previews; constraints and
interpretation in `docs/PLANNER_RESULTS.md` and the previous full-domain plan.

## Constraints and engineering calls

- No human-selected strategy, weighted score, native rule change or model change.
- Names are selectors in the successor menu, not a promise of stable coordinates,
  building identity or availability. Never carry candidate objects between steps.
- Exact proposal keys: `decision_id`, `candidate_ids`, `reason`. One or two
  nonempty names (at most 128 characters); first name must be currently legal.
  Successor availability is deliberately unknown until simulated.
- Bound preview budget to 1..8000 ticks and per-step minimum to 0..800 ticks.
- Invalid successor returns the charged valid prefix with `invalid_successor`;
  terminal, failed and exhausted prefixes stop immediately. No unchecked fallback.
- Control runs for actual charged prefix ticks. Unequal early terminal durations
  are explicitly noncomparable. Invalid prefixes are never accepted plans.
- Preserve raw messages/rewards/actions and before/after forecast summaries,
  net treasury change (not quoted construction cost), six final diagnostics.
- These are engineering control fixtures, not model-proposed strategy evidence.

## Review focus

Stale observations or candidates; observation ticks exhausting the budget;
native terminal states; exceptions inside nested candidate previews or control;
state restoration that looks correct in scalar observations but changes replay.

## Tasks

- [x] RED: `python/test_compound.py` tests proposal bounds, successor regeneration,
  stale initial/successor state, invalid future selection, partial construction,
  exact tick accounting/control, terminal stopping and exception restoration.
- [x] GREEN: implement additive `python/julius_gym/compound.py`; preserve old CLI
  and candidate contracts. Run planner and replay unit suites.
- [x] Native: add explicit-path `python/test_compound_engine.py`, verify rollback
  against all six endpoints and fingerprint, replay raw actions from reset without
  generating any candidates, compare messages/rewards and all diagnostics.
  Save real controls through RunArtifacts and verify with independent replay CLI.
- [x] Review: fresh reviewer inspects code/tests/contracts and native evidence.
  Fix material findings with regression tests. Update results/TODO and API docs;
  commit only verified source/docs, leaving generated artifacts and staged models.

## Execution evidence

Baseline: 110 planner unit tests pass; native `test_forecast_engine.py` passes
with the existing training library and original assets. No dependency changes.
Decision: continue inline in the already authorized branch, as directed by the
previous checkpoint. Shell script ledger helpers are replaced by this document
on Windows; execution evidence is recorded below.

Implementation: initial tests fail for the missing compound interface, then 11
tests pass. Extended boundary coverage and per-stage diagnostics bring the suite
to 16 cases. Fresh source review identifies stale supplied observations, a reset
that could hide hidden-state rollback damage, missing intermediate peace ratings
and optimized Python bypassing native asserts. Regression tests reproduce the
stale-observation and missing observation/peace payload failures; the optimization
test fails before adding the guard. After corrections all 19 compound tests pass.
The native fixture now continues the plan from the restored state, with independent
fresh-process replay required for its archives. All stage scalar observations
(including peace), diagnostics and raw action messages/rewards are checked.

Verification: all 161 tests in every repository `unittest.TestCase` module pass,
including the existing planner and replay tests. `python -m pip check` passes.
Full `unittest discover -s python -p test_*.py` was attempted: seven pre-existing
CLI scripts (`test_env`, `test_multiple_resets`, `test_ppo`, `test_ppo_create`,
`test_ppo_learn`, `test_render`, `test_vecenv`) fail import because their required
path arguments are parsed at module scope; `test_import` fails printing Unicode
checkmarks under the Windows cp1252 output encoding. These are not compound test
failures. The complete unittest-class selection avoids importing those scripts;
native scripts are run explicitly with their required paths.

Ruling: expose existing native observation reader as `JuliusEnv.get_observation`
to reject stale scalar input before snapshot execution; no C/ABI change. Cost:
one read-only native observation call per preview. Retain full stage scalars and
diagnostics for auditability, accepting larger local preview payloads. No model
prompt changes or inference evaluation are included at this checkpoint.

Fresh review findings above are fixed; no deferred findings. Corrected native
fixtures pass six stage/final diagnostic checks, direct restored-state execution
and fresh-process replay for every branch. Every archive retains source snapshots
and SHA-256 hashes of source and the loaded library. Source changes are committed
separately from run artifacts and pre-existing staged models. Final evidence paths
and limits are maintained in `docs/PLANNER_RESULTS.md`.
