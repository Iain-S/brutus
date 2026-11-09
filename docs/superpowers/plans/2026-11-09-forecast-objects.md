# Forecast Objects Implementation Plan

> **For agentic workers:** Use executing-plans; keep this change confined to provider serialization, tests and documentation.

**Goal:** Make the captured-context representation probe reproducible through an opt-in adapter flag, without prescribing actions.

**Architecture:** Add `--forecast-format rows|objects` (default rows) to the
existing local adapter. Objects replace only candidate forecast value arrays
with dictionaries using the existing column names. Preserve every field,
including nulls and continuation statuses, and do not change model settings,
candidate order, validation or gameplay. Missing forecasts remain represented
by all-null fields. No forecast policy means no forecast representation.

**Tech Stack:** Python standard library and existing unittest suite.

## Design And Ruling

The user delegated continued experimentation without a prescribed build order.
Alternatives are larger models, policy/search changes or a representation-only
probe. Choose the smallest reversible interface change: offline probes already
showed sensitivity and higher forecast culture at three captured decisions,
but no live improvement has been established. Do not change the default, infer
causality from one trajectory, or prune alternatives based on short forecasts.
Named fields consume more context; retain the existing 4096 setting for now and
check prompt counts/server truncation before interpreting any live result.

## Steps

- [x] Add failing round-trip tests for fields/nulls/order, missing forecasts, absent forecast policy and default compatibility.
- [x] Add the opt-in request argument/CLI flag and audit metadata; run focused and complete planner tests.
- [x] Document the flag and limitations; review, commit and push source only.
- [x] Run one frozen 16-decision trial with only the format flag changed; verify strict independent replay and record prompt headroom/outcomes.

## Verification

`python -m unittest discover -s python -p 'test_planner*.py'`

Live settings match `planner-local_d4aa46fd`: instruction model, temperature
0.7, top-p 0.8, top-k 20, min-p 0, response 256, context 4096, HTTP timeout
170, runner timeout 180, 12800 ticks, 16 decisions, 800-tick interval,
1600-tick forecasts. Add only `--forecast-format objects`. Keep requests in
the standard run bundle, collect Ollama truncation entries and runtime identity,
then independently replay final buildings/food/population/victory. Any truncation
invalidates representation-only interpretation; record it rather than hiding it.

## Implementation Evidence

Three new tests failed before implementation (missing keyword/CLI flag), then
all 37 planner tests passed. Round-trip tests include missing forecasts, nulls,
truncated continuations, order and unchanged output schema/settings. The CLI
test verifies forwarding and stderr audit metadata. The implemented adapter
also reproduced all six offline request bodies exactly apart from the probe's
explicit seed. Default rows output remains unchanged.

Read-only independent review found no blockers, confirmed default compatibility
against HEAD, and passed all 37 planner tests. Implementation pushed as
`51aa6abd`, excluding the user's staged model files.

## Live Evidence And Next Checkpoint

Run `planner-local_b502c162` finished at 12800 ticks with 90 residents, culture
40, 30 food-holding residents and no win; all 16 decisions accepted, no fallback.
Ten schools were chosen, no general housing expansions. Final household/market
food was 97/488 units, granaries empty. Preview 131.2 seconds, inference 292.5,
total wall 426.5. Strict independent replay `replay_101295f6` passed including
the full food payload. Both bundles retain standard final saves; rendering
remains manual.

Six server warnings recorded original prompts of 4114-4204 tokens truncated to
4096. The source bundle's runtime sidecar retains these warnings, model digest,
GPU status and native-library hash. Accepted JSON is not evidence of intact
input. This trial therefore fails the context-headroom check and cannot support
a clean representation-only strategic comparison; completing the bounded run
and replay does not resolve that limitation.

Ruling: retain the default and stop spending live-run budget at this context
size. Next expose an audited context-size option without changing facts or
candidate availability; preflight the largest captured states with sufficient
headroom, then rerun under a separately recorded configuration. Keep the model,
adapter and executor frozen during each future live trial.
