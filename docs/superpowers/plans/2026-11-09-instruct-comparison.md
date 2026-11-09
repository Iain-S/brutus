# Compatible Instruction Model Comparison

> **For agentic workers:** Execute this bounded experiment without editing the adapter or executor during live runs.

**Goal:** Establish a valid local instruction-model baseline before changing strategy or placement behavior.

**Architecture:** Install the pinned Ollama instruction tag alongside existing
weights, verify its metadata/GPU operation and JSON command compatibility, then
run the committed planner unchanged. Compare recorded outcomes, not anecdotes;
require independent action replay including detailed food diagnostics.

**Tech Stack:** Existing Ollama service, Python command adapter and headless Julius.

## Fixed Configuration

- Model: `qwen3:4b-instruct-2507-q4_K_M`; record the installed digest.
- Sampling: temperature 0.7, top-p 0.8, top-k 20, min-p 0.
- Response budget: 256 tokens; HTTP timeout 170 seconds, runner timeout 180.
- Mission: peaceful Tarraco, normal campaign rules.
- Execution: 16 decisions, 12800 maximum paid ticks, 800-tick decision interval.
- Lookahead: 1600 minimum forecast ticks, bounded by remaining episode ticks.
- Existing candidate vocabulary, food diagnostics and four-cycle history unchanged.

The sampling profile and supported model mode differ from earlier trials;
results are not a controlled attribution of changes to model size alone.

## Checks

- [x] Finish download, retaining existing models and verifying installed metadata.
- [x] Check valid final JSON on captured contexts and GPU offload.
- [ ] Run the fixed experiment; inspect accepted/fallback choices and prompt truncation.
- [ ] Independently replay final building/food diagnostics, population and outcome.
- [ ] Record source/configuration, outcome metrics, end-save location and limitations.
- [ ] Commit and push verified source/documentation only; preserve staged models.

## Parallel Audit

A read-only audit found that the ninth starter macro routed an access road
through its own planned house tiles. This is not true housing exhaustion.

Ruling: fix this demonstrated legality bug before the first full instruction
trial rather than knowingly suppress a viable choice. Three regressions first
failed: a side-entry strip with no legal access, continued search to a farther
valid strip, and actual ninth-block construction in Tarraco. Reject access-path
intersections with the entire planned strip (including future road cells, to
avoid duplicate road construction), then continue the existing search. No
strategy or campaign rule is changed. Record the verified fix commit and freeze
the executor/adapter for the trial. This adds another configuration difference
from historical runs; do not attribute outcomes solely to model replacement.

## Preflight Evidence

Download completed with Ollama digest verification. Installed manifest digest:
`0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`.
The service reports completion/tools capabilities and verified GPU offload.
Three captured contexts returned valid current-decision JSON at prompt lengths
1036, 3075 and 3254 tokens. Choices are observations, not an acceptance test for
a prescribed strategy; none were executed. Existing models remain installed.

Both synthetic housing regressions and the native nine-block test now pass.
Baseline, food-supply macro, culture construction and food-query regressions
also pass. The remaining siting heuristics and six-by-three strip restriction
are not changed by the collision fix.
