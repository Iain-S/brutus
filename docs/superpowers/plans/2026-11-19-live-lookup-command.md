# Bounded Live Lookup Command Plan

> Execute inline with tests first, source-only commits and source review.
> Preserve user-staged models, historical runs and failed gates.

**Goal:** Connect the passing ID-only lookup interface to the existing command
runner, then evaluate eight actual native decisions with strict replay.

## Design And Constraints

Add a SEPARATE `python/examples/ollama_lookup_planner.py` command. Do not
repurpose old flags, change default requests or modify native gameplay. Reuse
the existing lookup/query/selection helpers, raw-context provenance validation,
inference guards and adapter-owned evidence. Both alternatives are selected by
the model from the complete legal set; no human ranking, scores or build order.

The command reads one JSON context and returns the existing three-key choice
only after full success and durable final audit. It attempts at most two API
calls, no internal retry. Defaults: 170-second per-call cap, 290-second total
acceptance deadline, 8K context, 256 output tokens and the pinned trial's
instruct sampling. CLI validates all settings and supports a local model tag
and audit root; no external-provider or server-configuration changes.

Archive every invocation separately under
`runs/planner-command-calls/YYYY-MM-DD/<UTC>_lookup_<uuid8>/`. Save exact input,
source snapshots/hashes, both requests/raw responses, native lookup, statuses,
attempted/returned API counts, timings, options, provenance and terminal error
or proposed choice. This is a model-command record, not a native game save.
Emit a small initial audit pointer on stderr so parent timeouts retain its
location. Emit a bounded terminal summary before success stdout; a failed or
late result must never print a choice. Audit-write failure also fails closed.
Process kills cannot guarantee a finalized manifest; leave progress evidence.

The runner retains two COMMAND attempts then explicit wait fallback. Its
`model_calls` field counts command invocations, NOT underlying API calls:
report both, with up to four API attempts per failed decision. Use an outer
`--model-timeout 300` for the 290-second inner deadline. Do not change runner
retry/action policy or infer API counts from command count alone.

## Tasks

- [x] RED: add `python/test_planner_lookup_command.py`. Test two-stage success,
  complete audit/source/context provenance, stdout's old schema, compact stderr
  pointer/summary; invalid query/choice/inference/duplicate or malformed API
  response; no second call after bad query; shortened remaining timeout and
  late-response rejection; no stdout/internal retry on error; audit-write and
  directory failures; invalid CLI options before network. Observe failures.
- [x] GREEN: implement the separate wrapper and document invocation/audit
  semantics in `python/examples/PLANNER.md` and command-call layout in
  `python/examples/RUNS.md`. Run focused planner/replay suites, review source,
  then commit/push source only before a native trial.
- [x] Verify the pinned installed model/digest, canonical DLL load, all seven
  native CTests and snapshot/reset boundary script. Do not repair trust by
  changing security policy or binary names. If native checks fail, stop live
  acceptance and preserve evidence rather than relaxing comparisons.
- [x] Run eight decisions on peaceful Tarraco with the committed wrapper:
  episode cap 12,800 ticks, cadence 800, forecasts 1,600, explicit library/data
  paths, pinned instruct model/sampling/context/output and 170/290/300-second
  API/command budgets. Keep all legal tools/native goals. Export normal native
  end save and all six diagnostics; real-assets PNG remains manual.
- [x] Independently replay every step/message/reward and all six endpoints,
  population and authoritative victory. Audit every command/API/fallback/error,
  evidence ownership/provenance, latency and token budgets. Compare actual
  matched 6,400-tick measurements against existing baseline prefixes; do not
  claim repeated controlled strategy evidence or a win from a partial run.
  Review, record limits/next checkpoint, commit/push documentation only.

## Runtime And Provenance

Keep input validation errors in the exact saved command context, including
the runner's per-attempt `validation_errors`. Its fingerprint can differ from
the base decision context even without native advancement. Link each parent
attempt to its initial/terminal stderr audit directory; do not fabricate a
matching hash by omitting fields. Terminal summaries must fit the runner's
2,048-character stderr capture; full detail belongs in command artifacts.

Passing frozen selection did not prove model understanding or action quality.
The previous byte-identical query stage was faster under uncontrolled runtime
conditions, so no schema-only latency claim. A native run is a distinct
evaluation with larger 290/300-second aggregate budgets than the historical
one-call profile. A replay match verifies execution, not strategic optimality.

The user requested this next checkpoint and delegated continuation/integration.
Use the existing authorized branch/workspace and explicit source-only commits;
no worktree switch, repeated design question, new model installation or
environment change. Never stage generated audits, game assets, weights or
personal configuration. Preserve unrelated staged model files unchanged.

## Source Verification

Observed RED for the missing command, then GREEN for its lifecycle boundary.
Fresh review reproduced three additional gaps: only a socket/whole timeout
instead of elapsed per-API acceptance, malformed API bodies lost before
return accounting, and prepared audit-write failure counted as an attempt.
New failing regressions precede fixes: hard 170-second maximum plus elapsed
per-API checks, raw `.response.body` capture/return counting before parsing,
and durable preparation before transport-attempt counting without intervening
fallible audit I/O. Killed prepared records can have unknown actual transport
counts; they are not silently treated as zero.

All 105 focused planner and seven replay tests pass, including 14 command
cases. Source re-review finds no remaining issues. The Windows sandbox denies
child access to restrictive-mode tempfile fixtures; tests use owned inherited-
permission workspace fixtures with checked cleanup instead. No ACL/security
configuration changes were made. Native health and trial acceptance remain
separate, pending checks; no outcome follows from these mocked unit tests.

## Native Trial And Replay: 2026-11-19

On committed wrapper `fa5ec135`, `planner-local_d54f5084` completes eight
decisions / 6,400 native ticks with the unchanged 12,800-tick episode cap,
800-tick cadence and 1,600-tick previews. Native goals/rules/tools are unchanged.
Before launch, the canonical unchanged DLL loads, all seven native fixtures
pass and snapshot/reset/terminal/year-wind boundary checks pass. The installed
instruct-model digest matches the pinned profile; no security/server/model
configuration or native code change is made.

All eight COMMAND invocations succeed, each with two returned API bodies:
16 actual API attempts/responses, zero retries, validation failures, timeouts
or wait fallbacks. Query inputs are 2,618..4,713 tokens, outputs 22..29; final
inputs 2,958..4,431, outputs 17..20. Child command durations are about
35.9..58.0 seconds within both deadlines; parent inference totals about
422.8 seconds, previews 75.9, actual execution 1.4. Different states, commands,
budgets and uncontrolled runtime preclude a clean causal latency comparison.

The independent command audit joins each parent's received stdout/return status
and stderr pointer to its child manifest, source hashes, exact context,
request schemas, raw bodies, native lookup, provenance, stage timing and
adapter-owned evidence. Per-attempt validation errors are retained in context
hashes rather than omitted to create a false match. All summaries fit the
2,048-character parent stderr capture. Command invocation count is not
misreported as API count; child evidence does not itself imply execution.

Choices are housing, market, market, water supply, gardens, market, gardens,
housing. Every macro finishes successfully. There is no victory; the run stops
for its decision budget, not episode truncation. Independent `replay_a909eb19`
matches every primitive action message/reward, all six final diagnostic
payloads, population and authoritative victory state. Matched
`planner-prefix-review_0a31f0cf` independently measures the full trace. All
three campaign bundles are under `runs/tarraco/2026-11-19/`, finish without
artifact errors and retain native end saves/all six diagnostics. Real-assets
PNG capture remains manual and pending.

Source-run `evaluation-audit.json`, `evaluation-comparison.json`,
`evaluation-availability.json`, `evaluation-environment.json` and the audit
source retain the detailed evidence. Child command archives are linked through
each action-log attempt; no game save or screenshot is fabricated there.

| Actual Measurement At 6,400 Ticks | Short-Reason Rows | Reason-First Rows With Fallbacks | Reason-First Overrides | Lookup Selection |
| --- | ---: | ---: | ---: | ---: |
| Population | 39 | 218 | 284 | 56 |
| Culture | 0 | 0 | 0 | 0 |
| Prosperity | 0 | 0 | 0 | 0 |
| Peace | 0 | 0 | 0 | 0 |
| Favor | 50 | 50 | 50 | 50 |
| Health | 50 | 44 | 44 | 50 |
| Treasury | 7,542 | 6,977 | 6,373 | 7,234 |
| Residents With Food | 0 | 0 | 0 | 0 |
| Residents With Fountain Access | 39 | 0 | 0 | 42 |
| Maximum House Level | 1 | 1 | 1 | 1 |
| Collected Tax Denarii This Year | 0 | 0 | 0 | 0 |

The first three columns use the prior matched prefix reviews `c5e9a958`,
`d3810ac3` and `5eb8f93e`, not the older 16-decision final population.
The rows reason-first run has three wait fallbacks. This is not a repeated,
seed-controlled strategy ablation. The new city has ten occupied houses,
six desirability-blocked houses and native cached prosperity cap 7, but
actual prosperity remains zero. Water access and healthy population do not
establish multi-goal competence: food delivery, culture and tax collection
remain zero, and three markets were built without a food source.

### Shortlist Diagnosis And Next Checkpoint

The complete wheat-supply macro is legally offered in ALL eight contexts;
cultural service macros are offered from decision 1 onward. The model never
queries either the wheat macro or any of those culture macros. Markets and
one granary DO appear in queries, so this is not a claim that all food-related
tools were ignored. Legal construction preview does not guarantee staffing,
coverage or benefit, but the missing options are not hidden by the executor.

The final model is restricted to its own two queried alternatives. Thus its
shortlist structurally excludes those food-production/culture possibilities
from final choice on this trace. This is model-directed, not a human winning
order, but it is now a concrete planning-breadth bottleneck. Do not promote
the policy or extend it unchanged toward a full campaign win from this result.

Next, test a DISTINCT full-domain final-selection interface on the matched
frozen contexts: retain the same model query and native lookup but also keep
the complete legal menu/forecasts visible and selectable in the final stage.
Do not force food/culture, rank actions or change game rules. Any selected
candidate's evidence must still derive independently from the original native
context, including when not in the earlier query. Preserve the existing
queried-membership contract as-is; a broader domain needs its own tests and
explicit audit semantics, not silently bypassing a guard.

Compare frozen selections before another live evaluation. This tests a
measured search-breadth limitation, not another cosmetic formatting claim.
If full-domain choices still ignore unmet goals, investigate multi-step
planning depth/model capability rather than treating further fact transport
as strategy optimization. No broader selector or winning policy is implemented
by this checkpoint.
