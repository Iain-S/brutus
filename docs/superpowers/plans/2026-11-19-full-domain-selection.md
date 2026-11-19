# Full-Domain Final Selection Plan

> Execute inline with tests first, source-only commits and fresh source review.
> Preserve staged models, old membership contracts and historical evaluations.

**Goal:** Test the breadth limitation measured in native `planner-local_d54f5084`:
wheat/culture tools were legal but absent from the model's own two-ID queries,
making them unavailable to the final selector. Test access, not a winning order.

## Separate Contract

Add pure helpers `full_domain_lookup_selection_request_body` and
`adapter_owned_full_domain_choice` to `ollama_planner_lookup.py`. No existing
helper/CLI behavior changes and no new live flag. Validate the original lookup
and context hash as before. Retain the COMPLETE original compact menu, order,
all forecast values/types and common context in the final prompt, plus the same
model-requested native lookup. Permit every current legal ID in the two-key
final schema, including IDs not queried. No human shortlist, preferred action,
goal weights, forced food/culture or native rule/population change.

Check exact keys/types/current identity and selected current membership.
Attach explicitly adapter-owned evidence with
`selection_domain: all_current_candidates`, original query IDs and selected ID.
Derive comparison facts independently from the RAW context for queried IDs
plus the selected ID, deduplicated without changing query order. Never label
an unqueried selection as queried or fabricate model quotes. Preserve nulls,
provenance checks and the 2,000-character legacy reason bound. Existing narrow
selectors must continue rejecting unqueried selections.

The intervention changes BOTH final access to the complete menu/forecasts and
its output domain/instructions. It is not an isolated enum-only causal test.
Richer input may cost tokens/latency; retain the existing headroom guard. A
legal out-of-query selection would demonstrate broader access, not better play.

## Tasks

- [x] RED: extend `python/test_planner_lookup.py` for all-ID schema, full
  context/value/type/order retention across all formats, unchanged options,
  no mutation, selection outside the query, deduplicated raw-context evidence,
  explicit domain/ownership, invalid identity/types/keys/IDs, stale/tampered
  provenance, null/single wait/reason bound and unchanged old narrow behavior.
- [x] GREEN: implement only the two additive helpers. Document the experimental
  separate contract in `python/examples/PLANNER.md`; run focused planner/replay
  suites and direct old-request compatibility comparisons. Review then
  commit/push source before model probes. No live wrapper/domain toggle yet.
- [x] Run paired final-call-only probes on native decisions 1, 3, 5 and 7 of
  `planner-local_d54f5084`, using each command's EXACT saved context (including
  validation errors), recorded MODEL query and verified native lookup.
  Validate the query/lookup against its original source; no new/human query.
  Two repetitions of narrow/full per state make 16 API calls. Counterbalance
  profile order across states/repetitions; no retries, fallback or game action.
- [x] Keep the pinned instruct model/digest, sampling, 8K context, 256 output
  tokens and 170-second per-call acceptance cap. Record full requests/raw
  bodies/responses, token/latency/error telemetry, domain/ownership and source
  hashes. Query calls are REPLAYED FROM RECORDS, not executed or charged again:
  this is not an eight-decision or full two-stage transaction benchmark.
- [x] Independently audit all request facts/schemas/provenance and received
  selections/evidence, even when inference fails. Feasibility requires all
  eight full-domain calls accepted without unsafe headroom, timeout or repair.
  Report out-of-query selections and actual choices per paired state/repetition
  without inventing a quality score. Preserve failures and old narrow rejects.
  Review results and commit/push documentation; no automatic native promotion.

## Interpretation And Artifacts

Use `runs/planner-input-probes/YYYY-MM-DD/<UTC>_full-domain_<uuid8>/` with exact
source/protocol snapshots and context/query/lookup provenance, requests/raw
responses and independent audit. Mark `native_execution: false`,
`executed_choices: 0`, `query_api_calls: 0`. Reference the old verified trace,
save/replay rather than copying a save or claiming a new image/native state.

This compares model behavior on four targeted states, not causal strategy
improvement, general capacity or mission completion. Unseeded repeated answers
need not be independent; cache/runtime conditions are uncontrolled. Never count
a legal food/culture choice as successful delivery/ratings without actual
native execution/replay. If choices remain poor despite full access, investigate
planning depth/model capability instead of more transport-only experiments.

The user requested this checkpoint and delegated continuation. Use the existing
authorized workspace/branch and source-only integration route; no worktree
switch, repeated design question, provider/model installation or environment
change. Preserve unrelated staged models, original assets and all generated
run records outside commits. Engineering calls here are not user-prescribed
gameplay strategy.

## Source Verification

Five new cases fail for missing helpers before implementation, then pass with
the additive functions. All 110 focused planner tests and seven replay tests
pass, including 21 lookup cases. Coverage includes all formats/all candidates,
complete context/value/order retention, exact schema/type/identity checks,
out-of-query selection without forged query membership, raw-derived evidence,
deduplication, stale/tampered lookup refusal, unknowns/single wait and reason
size. The old narrow validator still rejects unqueried selections.

Fresh source review finds no issues and independently passes the same 117
tests. Thirty-six occupied-state existing query/quote/narrow request cases
and old materializations match `6d2dd334` exactly. No live flag, native or
default-command change occurs. Paired frozen feasibility remains pending;
passing helper tests does not establish broader model behavior or better play.

## Paired Frozen Result: Access Works, Behavior Remains Narrow

On committed helpers `cde48533`,
`runs/planner-input-probes/2026-11-19/20261119T173520.971552Z_full-domain_ab0ae6bc/`
retains all sixteen requests/raw HTTP bodies/parsed responses, four exact
source contexts, recorded model queries, verified lookups, source/protocol
snapshots/hashes and `evaluation-audit.json` with audit source. The source
queries match original child raw responses; they were NOT executed again.
No new native environment, game action, save, replay or screenshot exists.

All sixteen final calls complete normally and pass inference, provenance,
domain/schema and adapter-evidence checks: eight narrow and eight full.
The full-domain feasibility gate passes, with no retries, timeouts,
headroom/length rejection or repaired answers. All eight full-domain outputs
nonetheless select IDs already in the recorded query. None selects an
unqueried alternative, including wheat supply or culture services.

| Frozen Decision | Recorded MODEL Query | Narrow Choice In Both Repetitions | Full Choice In Both Repetitions |
| --- | --- | --- | --- |
| 1 | Water, Market | Market | Water |
| 3 | Water, Granary | Water | Water |
| 5 | Water, Market | Market | Water |
| 7 | Housing, Farmland | Housing | Housing |

There are four changed paired responses (decisions 1 and 5, twice each), but
all changes stay within the original query. Full totals are six water-supply
and two housing choices; narrow totals are four markets, two water-supply and
two housing. This does not support treating the hard membership restriction
as the sufficient explanation for earlier omissions. The richer final input
can affect choices without producing broader exploration or demonstrated
strategic improvement. It does not prove that no future state would benefit.

Narrow inputs are 4,185..4,428 tokens, full inputs 5,141..5,481. Both output
17..20 tokens under the unchanged 256-token cap. Narrow wall times range
7.3..42.1 seconds; full 10.3..41.5. Total final-call wall time is about 413
seconds. Adjacent identical requests can reuse cache; order is counterbalanced,
but these are unseeded repeated samples on four targeted states, not independent
episodes or a controlled throughput benchmark. Query API calls are zero;
sixteen final calls must not be presented as eight two-stage transactions.

### Independent Audit And Limits

The auditor verifies recorded-query provenance, native source hashes, all
twenty forecast fields/types and order, exact full/narrow schemas, retained
context, final membership, deadlines and generated native evidence. Narrow
requests are byte-identical to the original live command's final requests.
Full menus contain every original legal ID and forecast, without masking or
recommendations. A synthetic legal unqueried wait response passes with a
third native evidence row; tampered unqueried evidence and incomplete full
enums reject. These fixtures are NOT counted as real model responses.

The absence of outside-query selections therefore is observed model behavior,
not an untested claim that the helper permits such selections. Salience of
the retained lookup, model priors/capability, native forecast horizon and
long-term resource tradeoffs remain possible explanations. This experiment
changes menu visibility, domain and instructions together; no single causal
mechanism or optimality result is isolated.

A labelled post-hoc source check records that school/library/theater forecasts
show culture 15/20/25 in all four states, while the wheat macro's food stocks
and farm workers remain zero at this preview horizon. These are earlier
simulated source endpoints, NOT new delivered food, actual ratings or a
guaranteed best action. Do not infer a winning order or give the model a
forced cultural/food choice from those observations.

No live full-domain flag is added and no new native trial is promoted. Earlier
native outcomes remain population 56, fountain coverage 42, food/culture zero;
they are not relabelled as outcomes of these frozen responses. Old narrow
membership guards and all historical failed gates remain unchanged.

### Next Checkpoint

Do not keep treating prompt transport/access as the entire planning problem.
Design a bounded native rollout interface for MODEL-PROPOSED short multi-step
macro plans, rather than only one construction followed by idle continuation.
Compare explicit native goal/state outcomes and equal charged time without
human-ranked actions, weighted scores or a prescribed winning sequence.

First establish rollback and independent replay controls for compound plans,
regenerating legal candidates in each simulated successor state. Record costs,
staffing, food and rating outcomes, actual ticks and any failed construction;
never execute an unchecked future action merely because its first step was
legal. A later model-choice diagnostic can test whether those native future
consequences help, while model capability and lookup anchoring remain separate
hypotheses. No multi-step rollout or strategic fix is implemented here.
