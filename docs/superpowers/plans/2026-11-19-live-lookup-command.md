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
- [ ] Verify the pinned installed model/digest, canonical DLL load, all seven
  native CTests and snapshot/reset boundary script. Do not repair trust by
  changing security policy or binary names. If native checks fail, stop live
  acceptance and preserve evidence rather than relaxing comparisons.
- [ ] Run eight decisions on peaceful Tarraco with the committed wrapper:
  episode cap 12,800 ticks, cadence 800, forecasts 1,600, explicit library/data
  paths, pinned instruct model/sampling/context/output and 170/290/300-second
  API/command budgets. Keep all legal tools/native goals. Export normal native
  end save and all six diagnostics; real-assets PNG remains manual.
- [ ] Independently replay every step/message/reward and all six endpoints,
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
