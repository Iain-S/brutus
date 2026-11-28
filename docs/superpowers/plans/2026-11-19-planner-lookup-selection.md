# ID-Only Lookup Selection Plan

> Execute inline, tests first, explicit source-only commits and one fresh
> source review. Preserve staged models and all historical failed gates.

**Goal:** Test the user-requested smaller final-response contract after the
four lookup transactions timed out. No live integration or native actions.

## Contract

Retain the existing stage-1 request, model-selected query IDs, materialization,
all native facts/provenance, common stage-2 context and inference settings.
Add separate pure helpers in `ollama_planner_lookup.py`:
`lookup_selection_request_body` and `adapter_owned_lookup_choice`.
The new stage-2 response has exactly `decision_id`, `candidate_id`, restricted
to the model's queried IDs. No model-written numbers, comparisons or rationale.
Reject wrong types/keys/identity/membership, not silently ignoring extras.

Before returning a choice, revalidate the full lookup and context fingerprint
against the original raw context. Attach comparison facts freshly derived from
that raw context in a legacy three-key response whose JSON `reason` explicitly
labels `evidence_origin: adapter`, context hash, queried IDs and native facts.
Respect the existing 2,000-character reason bound; never truncate evidence or
substitute a different action. Null remains unknown, not fabricated zero.

This is intentionally NOT the verified-quote contract. Do not synthesize absent
model quote fields and call them verified model evidence. Numeric provenance
can be correct even if the model does not understand it or chooses badly.
No ranking, weights, human shortlist, winning order, population cap or game
rule change. Preserve all old helper/adapter request bytes and semantics.

## Tasks

- [x] RED: extend `python/test_planner_lookup.py` for the new two-key schema,
  unchanged stage-2 facts/options/model-only ID restriction, exact selection
  checks, adapter-labelled independently derived evidence, immutability,
  stale/tampered data, single wait/unknowns and reason-size refusal. Confirm
  missing-helper failures before writing product code.
- [x] GREEN: implement only those pure helpers; document the separate
  ownership/acceptance contract in `python/examples/PLANNER.md`. Run all
  focused planner/replay tests and compare existing occupied-state helper
  requests against `2dde1838`. Source review, then commit/push source only.
- [x] On committed helpers run four frozen transactions on the SAME source
  decisions 5 and 7, two repetitions each. At most two API calls/transaction,
  zero retries/fallbacks/actions. Keep the pinned model, sampling, 8K context,
  256 output-token cap, 170-second per-call cap and 290-second whole-transaction
  acceptance deadline from the previous two-stage probe. Record both stages,
  native lookup, per-call/cumulative latency, errors and actual API counts.
- [x] Independently audit every saved request even on missing responses;
  verify raw-context facts/types/provenance, exact final selection and evidence
  ownership, token/headroom guards and deadlines. Gate passes only if all four
  complete without rejection/timeout. Preserve failures; no longer budgets or
  concealed retries. Report latency/completion separately from policy quality,
  review results and commit/push documentation.

## Evaluation Limits

Compare to `fact-lookup_deb60310`: it had valid lookup requests/native facts but
no completed final API responses. This new output schema AND corresponding
instructions change; facts/query/options do not. It is not an isolated model
benchmark, and server load/cache/unseeded sampling may affect timings. A pass
would establish interface feasibility on two frozen states, not quote-reading,
strategic competence, general capacity or a mission win. No native trial or
live CLI follows automatically. Any future wrapper needs aggregate deadlines,
API-call accounting and the usual strict native replay before promotion.

## Artifacts And Workspace

Use `runs/planner-input-probes/YYYY-MM-DD/<UTC>_lookup-selection_<uuid8>/` with
`native_execution: false`, `executed_choices: 0`, source hashes/snapshots,
lookups, full requests/raw responses and an independent audit. Explicitly
record `evidence_origin: adapter` and this contract's name. Reference the old
verified native trace/save/replay; no copied save or fake screenshot.

The user requested this next checkpoint and delegated continued investigation.
Continue the existing authorized branch/workspace; keep defaults, old quote
validators, environments, model/server configuration and native rules intact.
No worktree switch or repeated integration question. Commit only source/docs;
leave user-staged models, generated artifacts and original assets untouched.

## Source Verification

Six new cases fail for missing helpers before implementation, then pass with
the additive pure functions. All 91 focused planner tests (16 lookup cases)
and seven replay tests pass. Coverage includes exact schemas, unchanged
stage-2 facts/options, explicit native ownership, raw-context evidence,
immutability, unknowns/single wait, stale/tampered/unqueried/extra-quote
refusal and the legacy reason-size limit.

Fresh source review found no issues and independently passed the same 98
tests. Twelve occupied-state existing query/quote request bodies (both states,
three formats, two stages) and old materializations match `2dde1838` exactly.
The original adapter/default commands and old strict quote helpers are
unchanged. Frozen feasibility remains pending; these tests do not establish
local-model completion, correct understanding or strategic improvement.

## Frozen Result: New Selection Gate Passed

Committed helpers `1b1b072a` were used for
`runs/planner-input-probes/2026-11-19/20261119T094407.578592Z_lookup-selection_cc5746dd/`.
The pinned model digest and source context/manifest hashes match. Exact probe,
lookup helper, adapter and protocol sources/hashes, both contexts, all eight
requests/raw responses, four native lookup records and independent
`evaluation-audit.json` with audit source are retained. There is no new native
environment, game execution, save, replay or screenshot.

All four complete transactions pass the NEW ID-only selection contract.
There are eight API calls, zero retries/fallbacks, zero inference/evidence
rejections, zero timeouts and zero executed actions. Both stages complete with
normal stop reasons and the original input-headroom guards. Every final
response has only the two allowed selection keys. Attached facts are labelled
adapter-owned; no absent model comparison is manufactured and called verified.

| Decision / Repetition | Model-Requested Alternatives | Selected ID | Total Seconds |
| --- | --- | --- | ---: |
| 5 / 0 | Farmland, District-0 Gardens | `landscape_district_0` | 66.8 |
| 5 / 1 | Farmland, District-0 Gardens | `landscape_district_0` | 62.6 |
| 7 / 0 | District-0 Water, District-0 Market | `add_market_district_0` | 63.6 |
| 7 / 1 | District-0 Water, District-0 Market | `add_market_district_0` | 63.7 |

Query inputs measure 5,586..5,813 tokens and outputs 23..27. Final inputs
measure 4,379..4,397 and outputs 18..19, under the unchanged 256-token cap.
Queries take about 37.6..41.8 seconds; final calls about 24.9..25.7 seconds.
Totals are 62.6..66.8 seconds per transaction and about 256.6 seconds overall,
within both the 170-second per-call and 290-second total limits. Legacy reason
records are 593..627 characters, retaining full labelled native evidence.

The independent auditor rederives all twenty forecast fields/types for the
requested alternatives and actual wait, costs, derived comparison facts and
context provenance directly from the original trace. It verifies all eight
requests, exact queried-ID schemas, retained common context, raw final
selections, adapter-owned evidence and deadlines. Synthetic missing-response
controls pass without invented answers, while altered enums, lookup/common
context and false model-origin evidence reject. Original source artifacts
and earlier failed probes are unchanged.

### Timing And Interpretation Limits

The original query stage is byte-identical to the earlier interface, yet it
also became much faster: about 37.6..41.8 seconds here versus 120.5..157.9.
Query prompt-evaluation telemetry drops from about 100.7..122.4 seconds to
24.0..26.3. The read-only server snapshots report the same model, 8K context
and offload sizes; no configuration was changed by this work. Runtime load,
cache or other conditions were not controlled. Do NOT attribute the entire
speedup or completed gate solely to the smaller response schema.

The preceding quoted-comparison transaction gate remains 0/4 timeouts, and
the preceding one-pass quoted-evidence gate remains 0/4 factual rejections.
This new gate checks a different task and factual ownership. It does not
establish independent reconstruction, understanding, correct action ranking
or a mission win. Repetitions choose identical IDs within each state; two
targeted frozen states are not a general policy benchmark. No proposed action
is executed, so there is no new population, service, culture, finance or
victory measurement. No live CLI/runner integration or default changes occur.

### Next Checkpoint

Implement a separately tested bounded command wrapper for this ID-only
interface, retaining full per-stage request/response provenance and explicit
API counts (not just command invocations), aggregate deadlines, failure audit
and no internal retry. Do not silently repurpose old quote-checking flags or
schemas. Verify native-library health before actual execution.

Only then run a short native trial with the existing matched budgets: eight
decisions, 12,800-tick episode cap, 800-tick cadence and 1,600-tick forecasts.
Keep all native rules/tools, no combat or prescribed build order. Audit
fallbacks, API calls and measured multi-goal outcomes; independently replay
every recorded step and all six final endpoints without loosening checks.
Retain the normal native save/review artifacts; real-assets PNG remains
manual. A successful wrapper or replay still does not prove strategic
improvement; compare actual 6,400-tick measurements, not model explanations.
This wrapper and live trial are proposed next work, not implemented here.
