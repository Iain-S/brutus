# Verified Planner Comparisons Implementation Plan

> Execute inline with test-driven development, source-only commits and one
> fresh final review. Preserve staged models and historical runs.

**Goal:** Add an optional adapter profile that accepts a model's choice only
after its quoted comparison facts match the frozen native forecasts exactly.
Continue the evidence-checking checkpoint requested after `67a0096f`.

## Design And Alternatives

Free-text reasons still misstate forecast benefits after correct targeted
extraction. More labels corrected duration answers but did not demonstrate
choice/reasoning improvement. Instead of another prompt-only change or
human-ranked action score, require verifiable facts while leaving selection
and the alternatives entirely to the model. This checks evidence, not optimal
strategy or every future consequence. No neural training or game-rule change.

Add `--verify-comparisons`, mutually exclusive with `--reason-first` because
this profile has no model-written reason. Keep default/rows/objects/overrides
and both legacy reason-profile request bytes unchanged when disabled. Do not
deploy the experimental duration-key rename as part of this change.

The new model response is ordered `comparisons`, `decision_id`, `candidate_id`.
Comparisons contain exactly two distinct model-selected legal alternatives,
or one if the only available candidate is wait. The final selected ID must
be among those compared; every original candidate remains selectable.
Each comparison has these exact fields:

`candidate_id`, `macro_ticks`, `forecast_ticks`, `population`, `culture`,
`prosperity`, `food_stocks`, `blocked_houses`, `blocked_vs_wait`.

Time fields quote the candidate macro preview and the forecast's actual
elapsed ticks. Other fields quote absolute projected endpoints;
`blocked_vs_wait` is projected blocked houses minus the actual wait forecast.
Values are integers or null for unknown data, never coerced from bool/string/
float or invented as zero. Require forecast mode, unique legal IDs and a real
wait projection; reject malformed reference data before inference. No expected
numeric-value enums, rankings, weights, worked answers or preferred tools.

After normal inference/headroom checks, validate exact response keys/types,
decision identity, comparison count/distinctness/membership, selected membership
and every quoted value against the ORIGINAL context, not model output or the
packed request. Reject mismatches rather than repairing them. Null matches
unknown, not proof of a known outcome. Duplicate JSON keys are invalid.

Translate accepted evidence to the existing three-key command response. Its
`reason` is adapter-generated JSON text containing the verified comparisons,
not a free-text model justification or strategy score. Keep the native runner
and its two-attempt / explicit-wait-fallback behavior unchanged. The adapter
performs no internal retry. Detailed mismatch information is audited on stderr;
the current runner still supplies its generic command-failure message on retry.
This limitation must be documented rather than silently changing runner policy.

## Tasks And Files

- [x] RED: `python/test_planner_verified_comparisons.py` covers schema/order,
  all IDs/options/context preservation, disabled legacy fixtures, complete
  valid/unknown/single-wait responses, every scalar mismatch and invalid
  type/keys/ID/count/duplicates/chosen-not-compared case. CLI tests cover
  translation, audit before rejection, unchanged inference guards, no stdout
  on failure, no internal retry and conflicting flags. Observe failures.
- [x] GREEN: minimal helpers in `python/examples/ollama_planner.py` for
  reference/schema construction and evidence validation/translation; add the
  optional keyword/CLI path without default request or runner changes. Run
  all focused planner/replay suites and frozen legacy request fixtures.
  Document use, audited acceptance meaning, unknowns and retry limitations
  in `python/examples/PLANNER.md`. Review then commit/push source only.
- [x] On the committed implementation, run four input-only frozen probes
  (two repetitions on decisions 5 and 7 of `planner-local_03ba650f`) using the
  pinned instruct model, 8K context, 256 output tokens, existing sampling
  and 170-second API timeout. No hidden retry, model installation or native
  action. Save full request/response/evidence errors, options and source hashes
  under the established input-probe convention; no copied/fake native save.
- [x] Independently audit all comparison facts and output/headroom checks.
  Only four accepted responses without inference/evidence rejection pass this
  frozen feasibility gate. Do not loosen it, lengthen output or substitute
  corrected facts if the model fails. Record choice diversity separately
  from factual correctness; no strategy, victory or live outcome claim.
  Document results and next checkpoint, then commit/push documentation.

## Rulings And Constraints

The user has delegated continued investigation, selected local model commands
and requested this specific next checkpoint. Continue the existing authorized
branch/workspace with no worktree switch or repeated integration question.
Implementation choices above are investigator decisions, not user-prescribed
strategy. All original assets, environments, model weights, local configuration
and probe outputs remain excluded from commits. A live trial requires a
separate bounded decision with all six strict replay endpoints; frozen
evidence validation alone is not enough to claim competent campaign planning.

## Source Verification

Observed RED for missing helper/keyword/CLI behavior, followed by GREEN for
the minimal optional implementation. Fourteen new tests now pass with 75
focused planner and seven replay tests. Four frozen legacy request hashes
remain unchanged; direct comparisons on both occupied source contexts cover
all three forecast formats and both old reason profiles (twelve byte-identical
request cases against `67a0096f`). No native source or runner behavior changes.

Fresh source review found one minor audit gap: absent/non-string API response
payloads failed closed but omitted the bounded validation error. Five new
malformed-payload cases reproduced the gap before an explicit string check;
the full suites pass afterward. The guarded profile now audits those errors
without sending a choice to stdout. No frozen model feasibility or strategic
improvement is claimed by the unit tests; the four-call gate remains pending.

## Frozen Feasibility Result: Gate Failed

Committed implementation `dbb70951` was used for all four requests in
`runs/planner-input-probes/2026-11-18/20261118T233333.128700Z_verified-comparisons_b8d3de13/`.
The pinned instruct-model digest and all original source context/manifest
hashes match. Exact probe/adapter/protocol sources and hashes, both frozen
contexts, full requests/raw responses, per-call errors and an independently
recomputed `evaluation-audit.json` with its audit source are retained. No new
native environment, action, save, replay, snapshot or screenshot is produced.

All four inference responses complete normally with `done_reason: stop` and
safe input headroom. None times out, retries or ends for output length. Input
counts are 5,668..5,895 and outputs 200..209 of 256; inference takes about 517
seconds including loading. These measurements do not prove arbitrary valid
comparison payloads or larger cities always fit the output/context budget.

**Zero of four responses passes evidence validation.** The predeclared frozen
gate therefore fails. No corrected values, relaxed checks, extra output
budget or fallback choices are substituted. The independent audit checks
every quoted field, not just the first mismatch reported by the adapter.

| Decision / Repetition | Raw Proposed Choice | Incorrect Scalar Quotes | First Rejection |
| --- | --- | ---: | --- |
| 5 / 0 | Wheat Supply | 4 | Forecast ticks 55 instead of 1,600 |
| 5 / 1 | Wheat Supply | 4 | Forecast ticks 55 instead of 1,600 |
| 7 / 0 | Wheat Supply | 5 | Forecast ticks 72 instead of 1,600 |
| 7 / 1 | Water Supply District 0 | 13 | Forecast ticks 4 instead of 1,600 |

The first three responses compare wheat supply and district-0 gardens. Both
comparisons substitute macro duration for forecast duration. At decision 5,
the quoted blocked-versus-wait differences are 48 and 38, instead of 8 and -2;
those incorrect differences copy the absolute blocked-house counts. Decision
7 also invents garden culture 15 where the native projection is zero.

The fourth response compares water supply and a forum. It substitutes null
for known zero forecast fields, misstates population/blocked houses and
miscomputes a blocked-house difference, in addition to duration errors.
Missing overrides are baseline values, not unknowns: these are genuine
evidence mismatches, not merely cosmetic wording. The first two raw answers
repeat identically; the last two do not. Four calls on two targeted states
are not a general model benchmark or causal isolation of all failure sources.

Different raw proposals from the earlier housing-only profile are not
accepted policy improvements. None of these choices is accepted or executed;
there is no new population, service, finance, reward or victory result.
The optional implementation correctly rejects false evidence, but the tested
model/profile is not ready for a live trial. Defaults remain unchanged and
the flag stays an experimental boundary, not a promoted planner policy.

### Next Checkpoint

Do not weaken validation or run a native episode that would merely exercise
wait fallbacks. The failures include baseline/null interpretation and arithmetic,
not just duration naming. Test model-directed fact lookup in two stages:
the model first names legal alternatives, then receives fully materialized,
explicitly labelled native forecasts and wait-relative values for its own
requested alternatives before making the checked final choice. Any arithmetic
materialized by the adapter must remain separately validated against the raw
native context; it is not a model claim to silently repair after generation.

Keep the original complete candidate set available to the model's initial
query, with no human shortlist, ranking, action weights or build order. Record
both model calls, provenance, cumulative latency and failure/retry bounds.
Compare against this failed one-pass profile as a different interface, not a
retroactive pass of its gate. Design and validate the frozen interface first;
two-stage lookup is not implemented by this checkpoint, nor is a win implied.
