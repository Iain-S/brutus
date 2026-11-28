# Bounded Thinking-Profile Selection Capability Check

> Continue inline, tests first, fresh source review before inference. Keep the
> existing branch and preserve staged models and unrelated work. Source-only
> commits; zero native actions, no downloads, no environment/security changes.

**Goal:** Test whether the already installed thinking profile can complete a
bounded frozen selection task and, only if feasible, assess its order consistency.

**Spec:** `docs/PLANNER_TODO.md`, Selection Capability And Native Planning.

## Profiles And Frozen Inputs

Use the exact decisions 2 and 3 from the verified native comparison and the
seeded order baseline at
`runs/planner-input-probes/2026-11-22/20261122T151628.185019Z_compound-order_4af8da6b/`.
Pin its manifest SHA-256
`2490f47392d19a36305b0cf83861ede35720ef1bca9bf29367e955d2eb1c06ed`;
revalidate original native/history pins, all fourteen baseline requests/answers
and source hashes. Copy the complete reference into the new archive before calls.

- Instruct control: existing model/digest, think=False, 256 generated-token cap.
- Thinking candidate: installed `qwen3:4b-thinking`, digest
  `359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7`,
  think=True, **1536 generated-token cap**.
- Both keep exact native facts, schema, labels, system/prompt content, seed
  20261122, temperature .7, top-p .8, top-k 20, min-p 0, context 8192, and the
  existing 170-second process/acceptance deadline.

This is a PROFILE comparison: weights, model template/defaults, thinking mode and
token allowance differ. It does not isolate the effect of thinking alone or
establish that a larger model is necessary. Inspect/store `/api/show` capabilities,
template/defaults and model digests before and after. The installed candidate
reports Thinking-2507, about 4B parameters and thinking capability. Official
[thinking API documentation](https://docs.ollama.com/capabilities/thinking)
and [versioned API types](https://github.com/ollama/ollama/blob/v0.16.2/api/types.go)
describe separate thinking/response fields. Retain thinking text as unverified
model output; do not turn it into verified reasoning or a human strategy score.

## Schedule And Gates

1. Recheck the instruct profile's exact original-order seeded requests on states
   2 and 3. Require the historical compound choices to reproduce before changing
   profiles; a drift or validation failure stops the check.
2. Thinking canary: state 3, original order, 1536 tokens and 170 seconds. Require
   complete stop telemetry, context headroom, nonempty separate thinking field,
   and valid exact ID-only answer. A token limit, timeout or malformed output
   FAILS feasibility; stop and preserve it, with no retry/repair/budget increase.
3. If the canary passes, finish all six row/schema permutations on each state,
   counting the canary as its original-order condition, and two exact repeated
   original-order controls. Alternate state order across permutation pairs,
   beginning with state 3; repeat controls finish state 2 then state 3.

Maximum: **16 inference calls** (2 instruct + 14 thinking), no query/proposal
calls, no game ticks or executed choices. If the canary fails, at most three
calls occur. All legal alternatives remain in every final domain. No live
planner or old diagnostic behavior changes.

Assess source validity, instruct reproduction, thinking feasibility, selection
consistency and native strategy progress as separate gates. Consistency is not
optimality. Historical baseline is not a full interleaved profile ablation, and
one seed/two targeted states/cache behavior limit causal attribution. No current
call demonstrates new delivered native outcomes.

## Implementation And Review

- [x] Add separate `python/examples/probe_compound_capability.py`, reusing the
  immutable frozen loader, order transform and strict audited transport. Do not
  weaken existing instruct/length/context guards. Test profile-only changes,
  balanced conditional schedule, source substitution, thinking field validation,
  partial failure preservation, unknown/missing audit accounting and no native init.
- [x] Run all unittest classes and fresh read-only review. Fix material findings
  with regressions, commit source before inference.
- [x] Execute the bounded check. Independently audit accepted AND failed gates,
  raw body/telemetry, reference integrity and counters. Preserve failed canaries.
- [x] Record the result and useful next step in results/TODO; keep generated
  artifacts local, preserve unrelated staged work, commit/push source/docs.

Review focus: profile identity/defaults, token caps counting complete generation,
partial reasoning being mistaken for a final answer, source drift, claiming
consistency from an incomplete sweep, missing call evidence, and silently raising
limits after failure. No preselected winning action is introduced.

## Ledger

Engineering choice: use the installed reasoning alternative, not download a new
model. Keep the practical 170-second cap and predeclare a 1536-token canary;
failure under these bounds is a feasibility result, not proof of inferior model
capability. The existing instructed policy remains unchanged throughout.

Fresh source review finds gaps in failed-attempt receipt accounting, premature
success gates, observed model metadata retention, reference condition/HTTP
inventory and an external-reference reread. Regression tests reproduce those
gaps before fixes. The reference now pins a deterministic digest across all 117
required evidence files (including raw responses, conditions and HTTP receipts),
in addition to its manifest/native-source anchors. Full request and response
validation remains mandatory. Expected baseline answers come from the verified
local copy, not the mutable original path.

Observed completion and repeat results are separate from verified gates. Final
gates are withheld if audit/reference/model-identity evidence fails, while raw
observations remain available. Model metadata is collected and stored before
validation, retaining observed wrong digests or missing fields. Required template,
defaults and capability evidence is checked. Metadata failures do not erase
otherwise verified inference counters. Failed calls also require terminal audit
status, matching request and independently written HTTP/partial-body evidence;
contradictory/missing evidence yields unknown counts and no verified success.

Focused capability tests pass all fourteen cases, including complete schedules,
length-limited/missing-thinking canaries, baseline drift, coherent reference
tampering, missing audit, changed identity, missing template and partial timeout.
The real pinned reference and both installed model/template profiles validate
without inference. No existing live selector, old diagnostic or source artifact
is changed. All 207 unittest cases pass. Model, reference and inference-audit
failures are separate finalization evidence; only missing/contradictory transport
audits make call counters unknown. Before/after observed metadata is retained even
when identity/default validation fails. Source integration precedes the canary.

Executed source `747ae57e`; archive:
`runs/planner-input-probes/2026-11-22/20261122T214852.589224Z_thinking-capability_0f329319/`.
Two instruct controls reproduce. The thinking canary stops after 19 tokens in
72.1 seconds with an empty final response and answer-shaped JSON only in its
thinking field. Strict parsing rejects it. Three calls/three responses total;
no retries, new native actions, budget exhaustion or conditional thinking sweep.
The independently audited record remains failed; selection consistency and
native progress are unassessed.

The original identity guard also mistakes reordered `/api/show` parameter
groups/generated Modelfile lines for a profile change. Independent diagnosis
confirms unchanged effective defaults, digests and templates, but does not
rewrite the archived gates. A failing regression precedes the future-only fix:
group display order is ignored, actual values and repeated-value order still
matter, and raw metadata is retained. Answer-shaped thinking remains invalid
as a final answer. All 209 unittest cases pass after these regressions/fixes.

Next is a separately bounded channel compatibility diagnostic, potentially
varying provider-side schema enforcement while retaining strict client final
JSON validation. No schema/template cause is established by this failed check.
Do not rerun this failed profile with larger budgets or promote its thinking
field. A valid final-channel completion must precede a balanced reliability
comparison. No model download or live policy change is justified here.
