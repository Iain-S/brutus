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
- [ ] On committed helpers run four frozen transactions on the SAME source
  decisions 5 and 7, two repetitions each. At most two API calls/transaction,
  zero retries/fallbacks/actions. Keep the pinned model, sampling, 8K context,
  256 output-token cap, 170-second per-call cap and 290-second whole-transaction
  acceptance deadline from the previous two-stage probe. Record both stages,
  native lookup, per-call/cumulative latency, errors and actual API counts.
- [ ] Independently audit every saved request even on missing responses;
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
