# Compact complete-menu implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement inline.

**Goal:** Retain every fact in the verified 45-root model input while reducing
repeated key tokens enough to resume bounded native decisions safely.

**Architecture:** A new ignored codec wraps the existing payload builder. It
aliases macro keys using an explicit reversible legend and transposes each
root's three sparse override dictionaries into field-wise three-value arrays.
Null means inherit that horizon's wait value; supplied native values are numbers
and may not be null. A separate decoder compares the expanded result with the
entire original input and independently checks every native cell and metadata.

**Tech stack:** Existing native DLL, Python, pinned temporary Pydantic AI
environment and local instruct model; no new installed dependency.

**Spec:** This document. User has authorized autonomous continuation; implement
in the existing experiment workspace, preserving unrelated work and old runs.

## Global constraints and design

Preserve every legal candidate ID and enum order, unavailable reason, macro
attribute, native field, base, goal, calendar and horizon. No root filtering,
ranking, weighted score, rules change, model-response repair or SDK retry.
New key legend: t=ticks, p=planned_ticks, cash=net_treasury_outlay,
actions=action_counts, target=target, ok=engine_preview_passed,
outcome=preview_outcome, benefit=benefit, savings=personal_savings_cost.
Unknown macro keys fail closed. Original order of dictionary keys is immaterial;
row and horizon order remain explicit. An override series must have length three,
at least one non-null numeric value, and no values equal to the corresponding
wait value. Original non-null values must be preserved exactly, including zero.
No synthetic/mock token count establishes real headroom.

## Review focus

- Null inheritance must not erase an explicit zero or negative value.
- Missing, extra, duplicated or transposed root/field data must fail decoding.
- Native metadata and enum domain must match the independently replayed case.
- Old error records remain failed, even if a new encoding works.
- Context growth in later states must stop the new run without shrinking menus.

## Task 1: Codec and independent evidence

Files: ignored `runs/compact_menu_codec.py`, `runs/check_compact_menu.py` and
`runs/audit_compact_menu.py`. Interface: encode(original_table) -> compact_table;
decode(compact_table) -> original_table. Original canonical table is built by
`candidate_only_continuation.payload(case, order)` and never edited.

- [x] Write failing tests for exact whole-table roundtrip on both verified
  34/45-root cases and A/B orders; explicit zero/negative inheritance and
  malformed legend, horizon, null, duplicate root and unknown-key rejection.
- [x] Implement alias mapping and field-wise series with null wait inheritance.
- [x] Verify every expanded native cell directly against branch checkpoints,
  all macro metadata against context, full legal domain against roots and replay.
- [x] Record exact text lengths; token counts remain unmeasured before inference;
  freeze one encoding without choosing based on model preferences.
- [x] Obtain fresh read-only review and commit protocol before live inference.

## Task 2: Separately bounded native pilot

Create ignored copies of the candidate-only runner/audit. Preserve source
16800-tick trace and verified 45-root inventory
`d6f738703dce5e43fc1f72ff130645db7d8d3ccde407fb574a6d4df40fd44f06`.
Host/request/state binding, strict schema and all native gates remain unchanged.
Only prompt encoding and its decoding instructions change. This is a new
experiment, not a retry or promotion of the previous context-limited record.

- [x] Mock full-domain typed A/B/A HTTP and audit requests/bindings/decoded facts.
- [ ] Run at most three new 800-tick decisions, nine model calls total, IDs 6–8;
  independent full-root six-month previews at every successor. Require three
  valid agreeing A/B/A selections and exact repeat bytes before each delivery.
  Stop on any failure/disagreement; no fallback, replayed answer or repair.
- [ ] Keep model weights/versions, seed 20261122, temperature .7, top_p .8,
  top_k 20, min_p 0, num_ctx 8192, max_tokens 256, effort none, 170-second deadline
  and 256+128 reservation. Actual prompt usage must be <=7808 per accepted call.
- [ ] Independently audit experiment receipts/model cleanup and replay the full
  actual trace with six diagnostics. Compare equal-time wait endpoints without
  scores. Report partial failures and no win honestly; commit/push own docs only.

## Ledger

Four codec tests fail on the initial no-op stub, then pass after implementation:
full original-table equality for 34/45 roots and both orders, zero/negative
values, invalid original values/keys and malformed compact payloads. The eleven
copied protocol checks pass with the new payload, including path-variable and
binding regressions. Independent audit has its own series/key expansion (does
not call the codec), compares the entire original payload and directly checks
all 2346/3105 native cells per 34/45-root request. Mock A/B/A bodies and schema
domains pass, with exact repeat bytes and distinct dispatches.

Mock archives: `runs/compact-menu-validation/20261127T122339.420281Z/` (34 roots)
and `runs/compact-menu-validation/20261127T122345.133032Z/` (45 roots).
Offline measurements and both original/compact tables:
`runs/compact-menu-preflight/20261127T122454.687736Z/`.
The 45-root user prompt shrinks from 19636 to 15640 characters (20.4%); the
34-root prompt from 14651 to 11173 (23.7%). These are character counts, not model
tokens or proof of headroom. A measurement attempt finds no tiktoken in the
canonical native environment; no package is installed to obtain an unrelated
tokenizer estimate. Actual response telemetry is still the acceptance gate.
Temporary model-environment `pip check` passes. No live calls made yet.

Fresh review finds two evidence gaps, fixed before inference: archive/hash the
old payload builder used by the auditor, and verify the imported baseline
matches that archived copy; make rejected-body/argument inspection best-effort
with raw SHA/length and parse-error evidence. A new integration regression first
reproduces the old JSON parsing crash, then passes for malformed complete body,
malformed tool arguments and a partial timeout body. Accepted-output validation
is unchanged; malformed data remains rejected. New helper:
`runs/check_compact_rejection_audit.py`. The original experimental builders and
auditors remain unchanged; fixes apply only to new copies.
Follow-up read-only review confirms both findings resolved and no further
material issues. All gates are ready for the separately bounded experiment.

Old partial and context-limited runs remain unchanged. Production planner and
dependencies remain unchanged.
