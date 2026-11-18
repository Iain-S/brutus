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
- [x] Recheck occupied-state headroom on the known 53-candidate context, with all values/types roundtripping. Retain actual model token telemetry and normal native endpoint saves; one-token output is not an accepted decision or a strategy trial. Do not infer general 2,500-person/eight-year capacity from one state.
- [x] Run a bounded eight-decision reason-first plus overrides trial with unchanged episode/cadence/forecast/sampling/output/time budgets. Audit every attempt and strict independent replay of all six endpoints. Compare matched 6,400-tick measurements and explicitly distinguish encoding changes, fallback behavior and strategy quality. Never promote on rationale claims or population alone; record results and next checkpoint, then commit/push documentation.

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

## Native Acceptance Resumed: 2026-11-18

The user reports disabling Smart App Control. The same canonical DLL now loads
successfully; no agent changed Windows security settings, native source or the
binary. All seven native CTests pass today, as do 61 focused planner tests and
seven replay unit tests. The installed instruct-model digest still matches the
pinned profile. The November 16 blocker above is historical, not current.

Production-encoder `planner-preflight_8acef130` replays the original five blocks
to 4,000 ticks / population 193 and checks the recorded native observations.
All 53 candidates, all 20 projected scalar values/types and nonforecast row
fields roundtrip. Input again measures 5,806 tokens with the required 256+128
headroom in 8K; actual output is one token, intentionally length-limited and
not an accepted choice. This cold probe took about 84 seconds; it is not a
controlled latency comparison. Fresh native saves and all six diagnostic
payloads are retained. Independent `replay_1046875b` matches every recorded
step, every endpoint, population and victory. Both bundles are under
`runs/tarraco/2026-11-18/`. This completes the occupied-state input gate, not
the pending strategy trial or a general full-city scalability claim.

## Bounded Live Trial: 2026-11-18

On source `7baadbd6`, `planner-local_03ba650f` completed eight decisions /
6,400 ticks, retaining the 12,800-tick episode cap. Cadence 800, forecasts
1,600, 8K context, output 256, reason-first, pinned instruct model/sampling
and 170/180-second timeouts are unchanged from the November 15 trial. Only
forecast format changes to `overrides`; all legal candidates remain visible.

All eight model calls were accepted: zero retries, rejected responses, wait
fallbacks or timeouts. Audited input counts are 2,611..5,832 and output counts
95..147; every completed request has the required output reserve and margin.
Across every recorded context, all candidate IDs/order, nonforecast row fields
and 20 projected scalar values/types roundtrip. Candidate counts by decision
are 8, 19, 30, 31, 42, 53, 53 and 47; there is no imposed population limit.
Inference took about 616 seconds and previews 137 seconds. Fewer calls and
different later states preclude attributing the runtime difference solely to
encoding efficiency. The model's stochastic choices were not seed-controlled.

Every selected action was `expand_housing`. The run has no native victory and
stops for its decision budget, not an episode cap or inference failure.
Independent `replay_7346dba4` matches all recorded step messages/rewards, all
six final endpoint payloads, population and authoritative victory state.
Matched `planner-prefix-review_5eb8f93e` independently measures the full trace;
all three new bundles finish without artifact errors. `evaluation-audit.json`
and `evaluation-comparison.json` are retained with the source run. All bundles
are under `runs/tarraco/2026-11-18/`; final native saves are available, while
real-assets `final.png` capture remains manual and pending.

| Native Measurement At 6,400 Ticks | Short-Reason Rows Baseline | Reason-First Rows With Fallbacks | Reason-First Overrides |
| --- | ---: | ---: | ---: |
| Population | 39 | 218 | 284 |
| Culture | 0 | 0 | 0 |
| Prosperity | 0 | 0 | 0 |
| Peace | 0 | 0 | 0 |
| Favor | 50 | 50 | 50 |
| Health | 50 | 44 | 44 |
| Treasury | 7,542 | 6,977 | 6,373 |
| Residents With Food | 0 | 0 | 0 |
| Residents With Fountain Access | 39 | 0 | 0 |
| Maximum House Level | 1 | 1 | 1 |
| Collected Tax Denarii This Year | 0 | 0 | 0 |

Baseline measurements remain the November 15 prefix reviews `c5e9a958` and
`d3810ac3`, not the older baseline's 12,800-tick final population. The rows
reason-first trace contains three wait fallbacks, so this is not a clean
strategy ablation. The new run proves bounded input transport and deterministic
execution, not better multi-goal planning or full-city context capacity.

### Next Checkpoint

Do not extend the housing-only run or promote reason-first from population
alone. First diagnose factual grounding on frozen recorded contexts without
executing new choices: can the model correctly read current population,
candidate duration, absolute forecasts and wait-relative differences? Keep
the same legal tools and objective; no preferred action, scoring function or
winning build order is supplied. Separate factual comprehension from strategy
before changing model, horizon, prompt or adding multi-step search.

For example, decision 7 calls wheat supply a 782-tick action, but its recorded
construction duration is 72 ticks. It also claims housing reduces desirability
blocks, although the forecast has 60 blocked houses versus wait's 53. The
current city already has population 245; decision 5's assertion that housing
is absent is likewise unsupported by its state (population 193). Treat reasons
as untrusted text, not validated measurements. This checkpoint can distinguish
misreading/unsupported claims from a policy that understands the data but
still overvalues immediate population growth. No change to native gameplay,
action availability, default adapter profile or existing validation is made.
