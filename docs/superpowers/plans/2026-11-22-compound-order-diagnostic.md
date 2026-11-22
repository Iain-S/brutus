# Frozen Compound Selection Order Diagnostic

> Continue inline, tests first and fresh review before inference. Preserve the
> existing workspace, staged models and historical source/evidence. No live
> policy changes or new native actions; source-only commits and integration.

**Goal:** Check presentation sensitivity in the last two audited compound
comparisons before attributing weak choices to model capability or horizon.

**Spec:** `docs/PLANNER_TODO.md`, Planning Quality Diagnosis.

**Source:** Compound native run
`runs/tarraco/2026-11-22/20261122T101738.483176Z_compound-model_11fb32a7/`,
decisions 2 and 3, source `03089798`. These are targeted problematic endpoints,
not a representative set of campaign states. No new root/successor proposals.

## Protocol

Keep exact frozen contexts, model-proposed IDs, native previews, provenance,
labels, all endpoint values/types and system instructions. Vary only the order
of the three comparison rows and the schema enum together. This tests combined
row/schema presentation sensitivity, not one independently isolated mechanism.
System label order and alternative semantics remain fixed.

Use the pinned installed instruct model/digest and previous .7/.8/20/0 sampling,
8K context, 256 output-token and 170-second process/acceptance bounds. Add seed
20261122 to EVERY request in this new profile. This is a new seeded diagnostic;
historical unseeded responses are not paired controls. Ollama 0.16.2 supports the
seed option; see [official versioned API types](https://github.com/ollama/ollama/blob/v0.16.2/api/types.go)
and [official API documentation](https://github.com/ollama/ollama/blob/main/docs/api.md).
Do not assume that supplying a seed proves determinism: test identical controls.

Schedule all six permutations, rotating state order between adjacent pairs.
Each alternative occupies each position twice in each saved state. Finish with
one exact original-order repeat per state: FOURTEEN final-selection API calls
maximum, zero query/proposal calls, zero retries, zero fallback, zero game ticks.
Stop on provenance/audit/inference failure; preserve the incomplete/failed gate.

Retain every request/raw body/response, timing/HTTP/strict completion telemetry,
source snapshots/hashes, source run references and per-condition source hashes.
Verify the original saved selection requests against reconstructed frozen data
before changing order. Independently audit allowed transformations and responses.
Report full order/choice table, selection positions, per-state counts, repeated
control agreement and explicit native endpoint/cost differences. No weighted
strategy score, fabricated model reasoning or claim of a new native result.

## Files and tasks

- [x] RED/GREEN `python/examples/compound_planner_order.py` and
  `python/test_compound_order.py`: additive ordered-request helper, exact permutation
  and seed validation, no mutation, complete content/type/provenance preservation,
  schedule balance and repeated-control identity. Old selector stays unchanged.
- [x] `python/examples/probe_compound_order.py`: frozen-source validation, immutable
  copied inputs, bounded schedule using existing strict audited transport, full
  lifecycle manifests/source hashes and fail-closed acceptance. Tests cover source
  tampering, invalid responses, audit failure and zero native execution.
- [x] All unittest modules and fresh source review; commit source before inference.
- [x] Run the fourteen-call diagnostic, independently audit, preserve all results
  and update results/TODO. No promotion to live campaign play.
- [x] Inspect native food/staffing and annual rating update code, documenting the
  timescale limits of this eight-month prefix before recommending longer trials.

## Review focus and interpretation

Swapped/dropped factual values, schema ordering that does not match menu order,
stale source inputs, seeded/unseeded attribution, failed repeatability controls,
miscounted API attempts, new native state falsely attributed to frozen calls,
and accidentally weakening the existing live selector's membership contract.

If choices vary, report observed sensitivity under this fixed-seed profile;
identical-control disagreement limits attribution to order. If choices do not
vary, order is not a sufficient explanation on these two states; neither model
capability nor horizon is thereby isolated. Fixed system label order, one seed,
two targeted states and uncontrolled cache/runtime behavior limit generalization.

## Ledger

Engineering call: add a fixed seed and two exact repeated controls to reduce
sampling ambiguity, rather than reinterpret the old unseeded run as an ablation.
No human action preference or winning sequence is introduced. All fourteen calls
are final-only input probes; the prior native save/replay remain the only native
evidence referenced by this experiment.

All 193 unittest cases pass, including eleven new order/probe cases. Real frozen
inputs validate before inference. Fresh review identifies source identity and
historical telemetry gaps, missing self-contained historical records, and missing
or contradictory accepted-call audits. Regression tests fail before correction.
The final loader pins seven original file-byte hashes (manifest, two requests,
two raw response bodies and two acceptance audits), checks strict model/completion
telemetry and type-sensitive request/answer consistency. The new archive copies
all required original records and sources, with hashes; tests validate it after
the original is made unavailable. Every started condition is durably recorded;
each accepted result requires matching accepted 1/1 call/response evidence.
Missing, truncated or logically contradictory audits produce unknown counts and
an error exit. Existing live commands, protocol helpers and source data are unchanged.

Native source inspection: `src/game/time.c` advances 50 ticks/day, 16 days/month,
12 months/year: 800 ticks/month and 9600/year. `src/game/tick.c` performs the yearly
ratings update at year rollover. `src/city/ratings.c` updates actual prosperity
and peace only on that yearly path. From zero peace/zero peace-years, the clean
illustrative sequence is 2, 4, 9, 14, 19, 24, 29, 34 over eight annual updates;
crime, destruction and riots can reduce progress. This is not a promised native
trajectory. The source run's eight months cannot assess annual rating progress.

`src/building/industry.c` instead requires houses covered and workers before
production progresses, adding worker-based work toward 200 raw-resource points.
Normal industry updates occur at daily tick 20, and eligible non-northern wheat
has an additional update at tick 46. Production has no annual harvest gate here;
staffing, cart generation and actual transport/delivery still take native time.
The source policy never builds a farm, so longer waiting alone cannot establish
its food-production competence. Do not attribute its zero food merely to an
annual harvest assumption or equate annual-rating delay with construction failure.

## Completed Frozen Result

On source `56519054`, archive
`runs/planner-input-probes/2026-11-22/20261122T151628.185019Z_compound-order_4af8da6b/`
retains all fourteen accepted final API calls and their raw evidence. There are
zero root/successor proposal calls, zero retries/fallbacks and zero native actions.
Both exact original-order repeats select compound, matching the first seeded
original-order calls. The historical unseeded decision-3 single choice is not
counted as a seeded control or a repeated result.

Balanced-block choices for decision 2 are compound twice/wait four times; for
decision 3, compound once/wait five times. Single is never selected. Position
counts across the twelve balanced calls are first 7, second 3, third 2. Thus
changing combined row/schema presentation changes choices under this fixed-seed
profile; it is not an always-first rule or a measured campaign improvement.
All native values/types and instructions remain intact. Root selection, search
breadth, horizon and model capability are not thereby isolated.

Independent audit validates the exact predeclared schedule, byte-identical
control requests, allowed transformations only, every raw/accepted selection,
strict telemetry/deadlines, immutable and copied source hashes and self-contained
historical evidence. Its source and JSON are retained inside the probe directory.
Calls take 22.2..52.5 seconds, 445.7 total; wall time is 452.4 seconds. Inputs are
5680..5866 tokens and every output is 15, under unchanged 8K/256-token bounds.
The results document contains the complete order/choice table and interpretation
limits. All 193 unittest cases pass. No live selector is promoted or changed.
