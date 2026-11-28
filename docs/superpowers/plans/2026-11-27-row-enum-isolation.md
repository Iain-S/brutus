# Forecast-row and tool-enum isolation plan

> **For agentic workers:** Use superpowers:executing-plans inline.

**Goal:** Determine whether the latest frozen-state presentation effect follows
forecast-row order, tool-schema enum order, or their combination.

**Architecture:** A separate ignored six-call diagnostic reuses the verified
45-root compact input and candidate-only transport. Change row and enum order
independently, retaining every fact, root ID and output gate. No native
environment is created, no save is advanced and no choice can authorize action.

**Tech stack:** Existing pinned temporary Python/Pydantic AI environment and
local instruct weights. No package installation or production dependency change.

**Spec:** This document; autonomous continuation is already authorized.

## Fixed design

Source case:
`runs/tarraco/2026-11-27/20261127T122823.764332Z_compact-menu-pilot_c8346456/case-00`.
Its 45 branches and 270 monthly checkpoints have independent native replay.
Pin forecast inventory to
`d6f738703dce5e43fc1f72ff130645db7d8d3ccde407fb574a6d4df40fd44f06`.
Pin the source finished run, failed-agreement audit and original model identity.

A means original order; B means its exact reversal. First letter specifies rows,
second enum. Run **AA, BB, AB, BA, BB, AA**, at most six new requests, one HTTP
attempt per worker. Final AA and BB repeat exact initial request bytes under one
temporary alias; unique dispatch bindings stay outside requests. All model and
serving settings remain unchanged: instruct weights, seed 20261122, temperature
.7, top_p .8, top_k20, min_p0, context8192, output256, effort none, deadline170s,
and reserved output+safety384. Every accepted prompt must use <=7808 tokens.
System text and row contents are unchanged. Only complete row order and schema
candidate enum order vary; names are never remapped. No scores, root filtering,
response repair, retries, native actions or majority vote.

Host fingerprint is archived **source** identity, not a claim about a live native
environment. Bind base/prefix/forecast inventory and unique dispatch to actual
request bytes; explicitly mark frozen-only scope. Keep full raw transport data,
model metadata/defaults, source copies/hashes and alias cleanup proof.

Stop on the first invalid/unsafe/timeout response or evidence/identity failure;
never silently fill missing conditions. Disagreement alone does not stop this
diagnostic because no execution gate is being evaluated. Model identity or
request-audit failures withdraw verified interpretation.

## Interpretation and review focus

Both exact-repeat controls must reproduce before classifying the four cells.
If AA=AB and BA=BB but the row groups differ, report an observed row-aligned
pattern; if AA=BA and AB=BB but enum groups differ, report enum-aligned. Otherwise
report all-same or mixed/interaction pattern. Any repeat disagreement prevents
that classification. These are observations on one state/seed and two order
levels, not general causal identification, model reasoning or policy quality.
Crossed cells have no repeats. No native strategy result can follow this probe.

Watch especially for coupled row/enum construction, changed non-order facts,
wrong/missing repeats, stale source provenance, malformed rejected bytes, and
claiming active native freshness from an archived fingerprint.

## Implementation and verification

New ignored helpers: `runs/probe_row_enum.py`, `runs/audit_row_enum.py`,
`runs/audit_row_enum_case.py` (independent copied table decoder), and
`runs/check_row_enum.py`. Preserve earlier sources and records.

- [x] Write failing intervention/classification tests; implement independent
  row/enum construction with exact complete-domain equality and fixed sequence.
- [x] Mock all six typed HTTP calls and one rejected-call stop; independently
  decode every native cell/metadata and inspect raw emitted enum order. Verify
  exact AA/BB request repeats, separate dispatch bindings, crossed-condition
  isolation and non-order request equality.
- [x] Obtain fresh read-only review, resolve findings and commit before inference.
- [x] Run the bounded diagnostic with actual telemetry; independently audit
  receipts, source/model identity, all native facts and cleanup. Preserve any
  failed/incomplete record; no native replay is invented for a no-action probe.
- [x] Report the matrix, repeat controls and limits; update results/TODO and
  commit/push only owned documentation. Preserve BRUTUS.md and staged models.

## Ledger

Two unit tests fail on no-op construction/classification stubs, then pass with
the implementation. They cover all four independent row/enum combinations,
whole-table equality after row normalization, unchanged system text, declared
six-condition sequence and every classification including unstable repeats.
Six mocked Pydantic AI HTTP requests pass full native-facts/metadata/wire audit:
`runs/planner-input-probes/2026-11-27/20261127T173839.191122Z_row-enum_3c312d7d/`.
Both exact-repeat bodies match and dispatch IDs remain distinct. Independent
decoder verifies all 3105 native cells per request plus original macro metadata.

A separate invalid-output mock stops after one request/response, with no retry
or missing condition filled:
`runs/planner-input-probes/2026-11-27/20261127T173920.639993Z_row-enum_4caacc6b/`.
Its rejected evidence independently audits, retaining null classification,
raw response/hash and rejection status. Compilation and temporary-environment
`pip check` pass. Mock token usage is synthetic; no actual headroom claim is
made from it. Fresh read-only review is pending before live inference.
Review identifies unguarded preflight and incomplete executed-helper provenance.
Fix before inference: save an initial manifest, guard setup/final source checks,
preserve unknown receipt counts, and emit explicitly unverified audit failures
with null classification. Archive/verify compound_planner.py, ollama_planner.py
and probe_root_horizons.py as well as the new scripts and prior builders.
A third regression reproduces the uncaught wrong-source-pin error, then passes
with a saved zero-call error record and unverified audit. Follow-up review finds
no further material issues.

Regenerated fixed-source mocks independently pass: complete six-call archive
`runs/planner-input-probes/2026-11-27/20261127T174203.126588Z_row-enum_347d7ec1/`
and stopped one-call archive
`runs/planner-input-probes/2026-11-27/20261127T174210.333058Z_row-enum_04355662/`.
All three construction/classification/preflight tests pass. Old mock archives
remain unchanged as evidence of their earlier source version. No new real
model requests or native actions yet.

## Actual outcome

Protocol commit before inference: `36251323`.
Archive:
`runs/planner-input-probes/2026-11-27/20261127T174321.052918Z_row-enum_e8ed8f11/`.
All six calls complete and independently audit. AA selects granary district2;
BB general housing; AB actor colony district2; BA farm-worker housing farm17.
Final BB and AA reproduce exactly, including request bytes. The predeclared
classification is mixed_or_interaction: four distinct choices, not a pattern
aligned only with rows or only with enum. The matrix establishes the observed
two-factor sensitivity locally, with the stated single-state/seed and unrepeated
crossed-cell limits; no general model reasoning or policy result is inferred.

Each request uses 7218 prompt tokens; completions 27/23/27/27/23/27. Each worker
finishes within 75 seconds, with no retries or invalid outputs. Independent
audit recovers all 3105 native cells and full metadata per table, checks exact
enum/row interventions and non-order request equality, model identity, archived
helper hashes and alias cleanup. Supplementary source-host comparison confirms
the archived fingerprint against the pinned original run record; it still
does not assert active native freshness. Evidence scripts and review JSON/CSV
are retained locally; `runs/summarize_row_enum.py` reports forecasts without a
score. All forecast endpoints remain counterfactual and no new native replay
is needed or claimed for this no-action diagnostic.

Next priority is separately scoped selector capability or a different selection
mechanism on the same complete native facts, preserving strict output and
execution gates. Do not promote any one of these differing answers, choose a
majority, or spend more calls on the unchanged thinking profile.
