# Lossless Forecast Overrides Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans with TDD, explicit source-only commits and one source review. Preserve staged models and historical runs.

**Goal:** Keep all legal candidates and their complete forecast values within the local model's context budget without changing native gameplay or ranking actions.

**Spec:** The context-overflow evidence and prototype in `2026-11-15-reason-first.md`.

**Decision:** Larger contexts already incurred substantial local memory/latency
costs. Limiting population or omitting tools is not acceptable. Choose an
optional, lossless forecast representation with an actual native wait forecast
as its shared baseline, not a synthetic modal state or hand-selected strategy.

**Architecture:** Add `--forecast-format overrides`, leaving rows/objects and
their request bytes unchanged. First construct the existing normalized scalar
forecast rows. After other prompt fields are assembled, replace each forecast
with named absolute overrides of the wait projection and append
`forecast_baseline` plus explicit semantics. Match the measured prototype's
request order/text where possible. Candidate IDs/order, all nonforecast fields,
options, output schema and reason-first selection remain unchanged.

**Encoding Contract:** The baseline holds all 20 currently emitted scalar
forecast fields, with `candidate_id: wait`. Reconstruct each full forecast by
merging baseline values with that candidate's overrides. Values are absolute
projected endpoints, NOT deltas or current state. Omitted keys equal baseline,
not zero; null remains unknown. Preserve scalar types (including bool versus
int), individual ticks/status and every value. If no wait candidate exists,
use an empty baseline with null candidate ID and full named projections, not a
fabricated wait forecast. If forecasts are disabled, emit no forecast encoding.
Do not add Pareto filtering, scores, recommended actions or population limits.

**Tech Stack / Files:** Existing `python/examples/ollama_planner.py`, focused
asset-free adapter tests, `python/examples/PLANNER.md`, run records and canonical
native simulation. No new dependency or native source change is needed.

## Tasks

- [ ] RED: test roundtrip equality with existing object projections across varied values, unknown/missing forecasts, empty/missing wait, bool/int distinction and changed time/status. Test all candidate IDs/order and nonforecast fields remain identical; no input-context mutation; forecasts-disabled behavior; unchanged default request bytes; CLI forwarding and audit metadata. Observe failures before implementation.
- [ ] GREEN: implement minimal optional encoder/CLI format. Keep existing context/output/server validation and bounded command auditing. Run the full focused planner/replay suites, compare request bytes to the measured prototype, review source, document semantics and commit/push source only.
- [ ] Recheck occupied-state headroom on the known 53-candidate context, with all values/types roundtripping. Retain actual model token telemetry and normal native endpoint saves; one-token output is not an accepted decision or a strategy trial. Do not infer general 2,500-person/eight-year capacity from one state.
- [ ] Run a bounded eight-decision reason-first plus overrides trial with unchanged episode/cadence/forecast/sampling/output/time budgets. Audit every attempt and strict independent replay of all six endpoints. Compare matched 6,400-tick measurements and explicitly distinguish encoding changes, fallback behavior and strategy quality. Never promote on rationale claims or population alone; record results and next checkpoint, then commit/push documentation.

## Existing Feasibility Evidence

`planner-preflight_6bf0bd72` on the reason-first failure context at 4,000 ticks /
population 193 preserved 53 candidates and roundtripped every scalar forecast
value/type. The input loaded at 5,806 tokens rather than the original 8,569
before truncation. This was one output token only; no choice executed.
`replay_a9fa89c0` strictly matches its recorded actions and all six endpoint
payloads. The prototype lives only in ignored run diagnostics, not production.
