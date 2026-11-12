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
- [x] Run the fixed experiment; inspect accepted/fallback choices and prompt truncation.
- [x] Independently replay final building/food diagnostics, population and outcome.
- [x] Record source/configuration, outcome metrics, end-save location and limitations.
- [x] Commit and push verified source/documentation only; preserve staged models.

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

## Trial Evidence

Source `061400a9`; run `planner-local_d4aa46fd`, replay `replay_3e8dcb85`.
All 16 decisions accepted, no fallback, 12800 ticks, 83 residents, culture 15,
seven food-holding residents and no win. Empty granaries, 172 market food units
and 28 household units remained. Five granaries, four markets and three schools
were chosen alongside housing/food-production actions. Peak prompt 2673 tokens;
no server prompt-truncation entries. Preview 125.8 seconds, inference 166.6,
total wall 295.2. Installed digest and native-library hash are retained in the
ignored source bundle's `model.runtime.json`. GPU offload verified.

Strict independent replay verified messages/rewards, final buildings, population,
victory and complete food diagnostics. Both bundles retain final saves; PNGs
remain pending manual Julius capture. Fresh verification also passed 34 planner
unit tests, six geometry tests and both native Gym CTests.

Ruling: do not spend a larger live-run budget on the same repeated construction
yet. First probe identical captured contexts with a named-field representation
of the same factual forecasts. No forced ordering or new strategic hints. This
can test an input-interpretation concern, not establish a full-game improvement.

Trial documentation committed and pushed as `84fea8cf`; staged model artifacts
were excluded and remain untouched.

## Offline Representation Probe

Three captured decisions (9, 12, 14) were each sampled once in both forms with
seed 42 and the trial sampling profile. Only candidate forecast arrays became
objects using their existing column names; all values, candidate order, other
facts, output schema and system instructions were identical. An independent
round-trip comparison verified equality. No game actions were executed.

Compact choices were granary, granary, school. Named-field choices were school,
school, theater in district 1. All six responses completed normally. Compact
prompts were 2506/2635/2673 tokens; named prompts 3447/3576/3614, all within the
4096-token setting, with no server truncation entries. Requests/responses are
retained under ignored `runs/instruct-representation-probe/`.

Ruling: do not deploy the representation change on this evidence. Choice
sensitivity does not establish improved outcomes; the named form also leaves
less context headroom. Before another live trial, probe the already-installed
thinking variant with thinking enabled and a bounded token/time budget. This
is a separate model/mode/budget experiment, not another representation pair.

## Bounded Thinking-Mode Probe

The installed thinking variant reports thinking capability. On captured decision
9 with named forecasts, thinking enabled, context 8192 and a 2048-token output
budget, schema-constrained decoding returned an empty final response. A short
JSON object appeared only in the thinking channel. Do not promote that object
to an accepted planner answer or interpret this as successful deliberation.
Removing only the `format` constraint then timed out after 290 seconds without
a completed response. Requests and diagnostics remain in ignored
`runs/thinking-mode-probe/`; no game actions or downloads occurred.

The constrained-output symptom is consistent with reported
[Ollama thinking/structured-output interactions](https://github.com/ollama/ollama/issues/10538),
but the local observations do not establish the precise server root cause or
prove that all model/version combinations fail. No service upgrade, response
channel workaround or adapter thinking-mode support was deployed. Return to
the supported instruction model for the bounded representation comparison.
