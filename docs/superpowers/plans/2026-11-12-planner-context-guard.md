# Local Planner Context Safety Implementation Plan

> **For agentic workers:** Execute inline with superpowers:executing-plans and TDD; preserve staged models.

**Goal:** Reject local-model decisions whose telemetry leaves insufficient context headroom, rather than treating potentially truncated input as a clean strategy trial.

**Architecture:** Keep request construction and model/provider settings unchanged.
Factor the adapter's existing result validation into a tested helper, requiring
positive integer prompt telemetry and reserving the configured generation
budget plus 128 tokens of extra context margin. This is a conservative rejection
test, not a tokenizer or proof that every possible server-side truncation is
detectable. Retain provider-independent execution and bounded fallback logs.

**Tech Stack:** Existing Python standard-library Ollama command adapter and unittest.

## Evidence And Scope

Housing and taxation capabilities are committed and independently replayed.
The occupied-state 16K probe timed out at 240 seconds, with 22/37 layers on GPU
and approximately 5 GiB total runtime memory. It returned no prompt token count
and is not a validated context or strategy trial. A separate 8K probe is running.
No automatic model installation, engine policy change or imposed build order.

## Tasks

- [x] Add failing tests for valid telemetry, missing/noninteger/nonpositive counts, insufficient headroom, exhausted output and server failure.
- [x] Implement the helper and invoke it before accepting JSON output; run all adapter/planner tests and source review.
- [x] Finish bounded occupied-state headroom probes with persistent endpoint saves; explicitly distinguish timeout, one-token probe and real accepted decisions.
- [ ] Commit/push only verified source/docs. Run a short model-selected experiment only after a usable headroom measurement; audit every call and replay its actions independently.
- [ ] If the fixed trial shows forecast-inferior repetition, evaluate forecast representation separately on a replayed frozen state; execute none of the probe choices and retain its normal final save/diagnostics.

## Probe Results

The timed-out 16K run is `planner-preflight_74bd5de9`, with final save and all
endpoint diagnostics retained and an explicit timeout error. Its incomplete
output is not an accepted decision or a strategy result.

Separate 8K `planner-preflight_11a5a4e8` replayed the committed paid taxation
fixture to tick 4,125, population 94, and previewed 33 candidates over 1,600 ticks
without altering the live state. Rows-format prompt: 12,675 characters, native
`prompt_eval_count` 6,797, one output token, approximately 39 seconds including
3.55 seconds loading and 32.46 seconds prompt evaluation. At 8K the server
offloaded 31/37 layers to GPU, versus 22/37 at 16K. No truncation warning for
this probe. The generation deliberately ended at its one-token limit; it is
headroom evidence, not an accepted JSON decision. Margin covers a 256-token
output plus 512 extra tokens for this one occupied state, not every future
prompt. Live trials must still audit each call and any fallback.

Independent source review found no blockers and confirms the guard is only a
conservative rejection check. It does not change provider/model settings or
engine rules. Unit coverage includes exact headroom boundaries, booleans/floats,
server/output-budget errors and CLI refusal to emit unsafe decision JSON.
All 47 planner/adapter unit tests pass. Metadata is emitted to stderr before
validation so rejected responses still retain token counts/options in the
existing bounded command audit; unsafe decision JSON never reaches stdout.

## Frozen-State Evaluation Design

**Blocked:** The fixed trial subsequently failed strict final-state replay.
Its forecasts may be contaminated by an unsnapshotted native water-worker
allocation cursor. Planning-quality inferences below are provisional, not a
validated model diagnosis. The representation probe was not executed. See
`2026-11-12-water-labor-snapshot.md`; first repair and prove determinism, then
capture a fresh clean frozen state. Do not reuse the polluted historical context
as a trusted counterfactual baseline.

The fixed trial is source `be4e2258`, 16 decisions / 12,800 ticks maximum,
800-tick decision cadence and 1,600-tick forecasts, instruct-model profile with
8K context, rows, max output 256, temperature 0.7 / top-p 0.8 / top-k 20 / min-p 0,
adapter timeout 170 seconds / runner timeout 180 seconds. Keep its inputs fixed.

Initial rows show some repeated water choices inferior to waiting on reported
forecast endpoints. A source/data review found no forecast-column alignment
defect. Some other water forecasts do improve future coverage; do not label
every repeated action useless. Short forecasts also fail to show food payoffs.

For a diagnostic after the fixed trial, freeze decision 3 by strictly replaying
its first three action blocks, verify the scalar observations match, and retain
all state facts. Restrict BOTH diagnostic conditions to the same four recorded
legal choices: housing, wheat supply, water supply and wait. This restriction
keeps named-object forecasts within 8K without the measured 16K memory/latency
penalty. It is an evaluation subset, never a deployed tool mask or game policy.

Make three requests per representation (rows versus named objects), alternating
which goes first, with identical model/settings/facts and normal validation.
Do not execute these choices. Persist raw requests/responses, choice audit and
the frozen endpoint save in `planner-choice-probe`. This tiny unseeded sample
can indicate representation sensitivity, not establish statistical significance
or full-action strategy quality. Reject telemetry/headroom failures explicitly.
