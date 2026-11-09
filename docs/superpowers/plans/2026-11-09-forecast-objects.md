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
- [ ] Document the flag and limitations; review, commit and push source only.
- [ ] Run one frozen 16-decision trial with only the format flag changed; verify strict independent replay and record prompt headroom/outcomes.

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
