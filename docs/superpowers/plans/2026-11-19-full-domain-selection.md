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
- [ ] Run paired final-call-only probes on native decisions 1, 3, 5 and 7 of
  `planner-local_d54f5084`, using each command's EXACT saved context (including
  validation errors), recorded MODEL query and verified native lookup.
  Validate the query/lookup against its original source; no new/human query.
  Two repetitions of narrow/full per state make 16 API calls. Counterbalance
  profile order across states/repetitions; no retries, fallback or game action.
- [ ] Keep the pinned instruct model/digest, sampling, 8K context, 256 output
  tokens and 170-second per-call acceptance cap. Record full requests/raw
  bodies/responses, token/latency/error telemetry, domain/ownership and source
  hashes. Query calls are REPLAYED FROM RECORDS, not executed or charged again:
  this is not an eight-decision or full two-stage transaction benchmark.
- [ ] Independently audit all request facts/schemas/provenance and received
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
