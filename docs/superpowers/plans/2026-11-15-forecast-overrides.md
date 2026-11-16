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

- [x] RED: test roundtrip equality with existing object projections across varied values, unknown/missing forecasts, empty/missing wait, bool/int distinction and changed time/status. Test all candidate IDs/order and nonforecast fields remain identical; no input-context mutation; forecasts-disabled behavior; unchanged default request bytes; CLI forwarding and audit metadata. Observe failures before implementation.
- [x] GREEN: implement minimal optional encoder/CLI format. Keep existing context/output/server validation and bounded command auditing. Run the full focused planner/replay suites, compare request bytes to the measured prototype, review source, document semantics and commit/push source only.
- [ ] Recheck occupied-state headroom on the known 53-candidate context, with all values/types roundtripping. Retain actual model token telemetry and normal native endpoint saves; one-token output is not an accepted decision or a strategy trial. Do not infer general 2,500-person/eight-year capacity from one state.
- [ ] Run a bounded eight-decision reason-first plus overrides trial with unchanged episode/cadence/forecast/sampling/output/time budgets. Audit every attempt and strict independent replay of all six endpoints. Compare matched 6,400-tick measurements and explicitly distinguish encoding changes, fallback behavior and strategy quality. Never promote on rationale claims or population alone; record results and next checkpoint, then commit/push documentation.

## Native Execution Blocker: 2026-11-16

The canonical Gym DLL now fails Python loading with Windows error 4551,
"An Application Control policy has blocked this file". Code Integrity event
3077 identifies the unsigned DLL and `VerifiedAndReputableDesktop` policy.
Its hash matches the previously verified binary; no native source or binary
changed in this checkpoint. Five standalone C fixtures time out even outside
the sandbox with 30-second limits; do not report those as passes. The normal
Python/Gym snapshot-boundary smoke fails at DLL loading, before episode setup.

Do not rebuild/rename the binary to evade the policy, change security settings,
or substitute another binary. Live replay, new endpoint saves and the strategy
trial require policy-compliant approval/signing of the native build. Read-only
diagnostics and the local hash/policy details are retained in ignored
`runs/overrides-native-block.json`; no machine-specific policy configuration
belongs in source commits.

Ruling: complete the unaffected Python implementation and model-input check
using the previously verified saved context. Clearly label that check as
saved-context-only; reference the old native save rather than copying it into
a new folder or claiming a fresh simulation/replay. Leave live acceptance
tasks pending until the native-library block is resolved.

## Existing Feasibility Evidence

`planner-preflight_6bf0bd72` on the reason-first failure context at 4,000 ticks /
population 193 preserved 53 candidates and roundtripped every scalar forecast
value/type. The input loaded at 5,806 tokens rather than the original 8,569
before truncation. This was one output token only; no choice executed.
`replay_a9fa89c0` strictly matches its recorded actions and all six endpoint
payloads. This pre-implementation prototype was retained in ignored diagnostics;
the optional implementation and current acceptance status are described below.

## Implementation Evidence

Observed failing tests for absent baseline encoding and CLI format choice.
The minimal optional implementation then passes 60 focused planner tests and
seven replay tests. Tests cover value/type reconstruction, null/missing data,
empty/unknown wait, time/status, unchanged candidate/nonforecast data and input
context, disabled forecasts, CLI audit/headroom refusal and four frozen legacy
request hashes (rows/objects with both reason profiles). Direct comparisons on
the occupied 53-candidate context confirm byte-identical legacy requests and
byte-identical overrides output to the measured prototype.
Fresh source review found no blockers and independently passed the nine new
tests and four baseline request fixtures. The 60 planner and seven asset-free
replay unit tests do not establish a fresh native simulation acceptance result.

Additional scalar hardening observed RED for signed floating zero: numeric
equality would elide a change from -0.0 to +0.0. Compare JSON representations as
well as scalar types; the new regression passes with 61 focused planner tests.
The measured native integer context still produces the exact same request.

Ruling: continue in the previously authorized feature branch and workspace,
preserving staged models and canonical paths. The Bash workspace helper again
failed its sandbox signal-pipe setup; use an equivalent plan-scoped PowerShell
ledger without changing Windows security settings.

## Committed Saved-Context Input Check: 2026-11-16

Implementation `945fb4c7` was committed/pushed before the input check. With the
native library blocked, the check imports only the adapter and uses the prior
verified context; it never creates a Gym environment or loads the DLL.

Model-only diagnostic `planner-input-probes/2026-11-16/` suffix
`overrides_33a1a19f` verifies all 53 candidate IDs/order, all 20 projected scalar
values/types and nonforecast row fields, and confirms the request is
byte-identical to the original prototype. The installed model digest still
matches the pinned instruct profile. The input again loads at 5,806 tokens in
8K, with room for a prospective 256-token output plus 128 extra. Actual output
is one token and intentionally ends for length; zero model choices are accepted.
The check took about 79 seconds, including loading/prefill. This is not a
like-for-like runtime benchmark against the earlier warm probe.

Metadata references the old native save and its prior verified replay, not a
newly generated save. No old save was copied into a new game run. The later
signed-zero hardening also reproduces that exact checked request. The current
input encoding is implemented, but fresh native endpoint capture, the planned
eight-decision trial and its independent replay remain pending. No campaign
progress, victory, or profile promotion is claimed for this checkpoint.
