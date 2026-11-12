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
