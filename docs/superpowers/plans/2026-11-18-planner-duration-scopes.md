# Frozen Planner Duration Scopes Diagnostic Plan

**Goal:** Test the duration-scope hypothesis from the completed factual
grounding diagnostic, then check transfer to action selection only if factual
reading improves. The user requested continuation of this checkpoint.

**Architecture:** An ignored input-only probe transforms the production
adapter's compact table reversibly. No deployed adapter, native gameplay,
candidate availability, objective, scalar value, model or budget changes.
Use the authorized existing branch and source-only commits/pushes; preserve
staged models and original run bundles. No new environment or native save.

## Hypothesis And Transformation

The earlier table scored 46/48 facts; named candidate dictionaries scored
40/48. Duration errors substituted 800, which occurs in execution cadence,
wait macro duration and recent outcome durations. This suggests scope
confusion but does not establish the cause of those errors or housing-only
play. Do not test another wholesale candidate layout or assume larger
contexts solve this.

Keep the existing positional table. Rename only duration labels:

- Candidate column `ticks` becomes `macro_execution_ticks`. This is NOT
  universally construction time: the wait candidate contains no construction.
- Forecast baseline/override key `ticks` becomes `forecast_elapsed_ticks`;
  update the existing forecast-semantics reference to that key.
- Recent-outcome column `ticks` becomes `cycle_executed_ticks`.
- Top-level `minimum_decision_interval` becomes `minimum_cycle_ticks`.
- Forecast-policy key `minimum_ticks` becomes `minimum_forecast_ticks`.

All values and ordering are retained. No worked examples, expected answers,
recommended actions, strategic scores, extra outcome forecasts or information
filtering are added. Invert the transformation and recover the original
request exactly, including scalar types and the complete candidate set.

## Frozen Protocol

- [x] Self-check transformation roundtrips and original-input immutability.
  Reuse the prior twelve factual questions/oracle unchanged, against decisions
  5 and 7 of verified `planner-local_03ba650f` (53 and 47 candidates). Verify
  every native forecast scalar/type and all non-duration fields independently.
- [x] Run eight factual calls: two states, original/scoped tables and two
  repetitions. Alternate label order. Same pinned instruct model/digest,
  sampling, 8K context, 256 output tokens and 170-second API timeout. Keep
  existing inference/headroom guard, exact schema/type checks, full raw
  responses and all failure evidence; no retries or executed choices.
- [x] Apply this predeclared gate: all four calls in each layout must pass
  transport and schema; scoped total correct facts must exceed the concurrent
  original
  total; scoped duration errors must decrease; no new non-duration errors
  may appear. Rejected calls do not count as correct answers. If the gate
  fails, do not silently change it or run the conditional transfer phase.
- [x] Only if the gate passes, run four further non-executing calls with the
  ORIGINAL reason-first choice schema/instructions: one original/scoped pair
  per frozen state, alternating order across states. Use every original legal
  ID in the schema and unchanged inference options. Validate response keys,
  current decision ID, listed candidate membership and reason type/length.
  No factual answers, diagnostic questions or earlier probe responses are
  supplied to these choice requests. No game action or planner fallback runs.
- [x] Independently audit saved request/response pairs, factual scores, gate
  decision, inference telemetry and any conditional choices. Report targeted
  factual improvement separately from reasoning fidelity, action diversity,
  actual execution and strategy quality. Review and commit/push documentation
  only; do not deploy duration labels from a tiny frozen sample.

## Evidence And Limits

Store `runs/planner-input-probes/YYYY-MM-DD/<UTC>_duration-scopes_<uuid8>/`
with `native_execution: false`, `executed_choices: 0`, source-context/action
hashes, protocol/source hashes, complete requests/responses and per-call audit.
Preserve exact probe/adapter sources with the run. Reference the verified
source trace and its original save/replay; do not copy a save or claim a new
native snapshot, replay or image. This is the same input-only convention as
the prior factual probe, not a campaign invocation.

Two targeted states and repeated stochastic samples are not a general model
benchmark or causal proof. Even if a scoped choice changes or its reason is
more factual, its forecast is a continuation without later construction,
not a mission-win guarantee. Failed or unchanged choice transfer is a valid
result. Larger planner changes require their own rationale and acceptance
gate, not hidden rollout, model installation or human-prescribed strategy.

## Completed Diagnostic: 2026-11-18

Protocol source `8a71e3cf` precedes
`runs/planner-input-probes/2026-11-18/20261118T154917.884494Z_duration-scopes_de2ca5ae/`.
Before inference, the gate was conservatively clarified to require four valid
original responses as well as four valid scoped responses, so rejected
baselines could not create an artificial factual improvement. The run retains
the exact pre-inference protocol copy/hash, probe/helper/adapter sources and
hashes, frozen contexts, all requests/responses, metadata and a separate
`evaluation-audit.json` with its audit source. Source action/manifest hashes
still match the verified campaign trace; no new native execution, save,
snapshot, replay or screenshot is claimed.

Self-checks verify byte-identical inverse requests, unchanged original input,
every candidate/non-duration field and all 20 native scalar values/types.
The factual questions/oracle are unchanged from `grounding_64250d06`; the new
original requests exactly match its saved table requests. Choice requests
retain the production reason-first schema/system and full legal-ID enum,
without the factual questions, expected answers or prior model responses.
Schema/choice checks and synthetic improvement/tie/incomplete/rejection gate
checks pass. The existing 61 focused planner and seven replay unit tests also
pass; native tests were not rerun by this input-only checkpoint.

All twelve calls complete normally (`done_reason: stop`) within context and
output budgets. None is retried, rejected, timed out or truncated. Acceptance
means inference/protocol validity, not truthful reasons or good strategy.

| Frozen Decision | Labels | Correct Facts In Each Repetition | Input Tokens | Output Tokens |
| --- | --- | --- | ---: | ---: |
| 5: Population 193, 53 Candidates | Original | 11/12, 11/12 | 6,025 | 125 |
| 5: Population 193, 53 Candidates | Scoped | 12/12, 12/12 | 6,036 | 124 |
| 7: Population 245, 47 Candidates | Original | 12/12, 12/12 | 5,798 | 126 |
| 7: Population 245, 47 Candidates | Scoped | 12/12, 12/12 | 5,809 | 126 |

The concurrent original totals 46/48 facts, reproducing the two housing
duration errors (800 rather than 25 at decision 5). Scoped totals 48/48, with
zero duration or non-duration errors. The predeclared gate therefore passes.
The scoped keys add eleven input tokens on each tested context. Factual
inference takes about 737 seconds; the conditional choice phase takes 352,
about 1,089 seconds combined including loading. This is not an isolated
latency benchmark. Factual answers repeat identically within every state/label
pair; do not treat repetitions as independent statistical evidence.

### Conditional Choice Transfer

One original/scoped choice pair is queried per state, reversing order for the
second state. All four proposals select `expand_housing`. Their input counts
are 5,579..5,817 and outputs 98..151 tokens. None is executed, so there is no
new live population, reward, service, finance or victory measurement. Unchanged
choice alone is not proof that a choice is good or bad.

Free-text factual fidelity does not reliably transfer. For decision 5, the
original reason calls 45 desirability-blocked houses a reduction, although
wait projects 40. For decision 7, the scoped reason calls 60 a reduction,
although wait projects 53. That scoped reason also claims farmland adds farm
workers/improves food; the recorded farmland continuation has zero farm
workers and food stocks. These claims are not supported by the reported
endpoints, even though targeted scope-labelled arithmetic/extraction was
correct. The scoped reason's prosperity benefit is likewise not established
by an endpoint prosperity value of zero.

This supports using scope-qualified duration labels for further testing,
not a production change or a demonstrated strategic improvement. It does not
identify a general causal mechanism for erroneous explanations or housing-only
play: only two states, two factual repetitions and one choice per label/state
are tested with unseeded sampling. The extraction and choice output tasks
differ, and a forecast assumes no later construction. All deployed adapter
options/defaults and native gameplay remain unchanged.

### Next Checkpoint

Do not spend another live housing-only episode treating clearer labels as a
policy fix. Test machine-checkable factual comparisons before a final choice:
let the model choose the compared legal alternatives, and verify their quoted
native forecasts exactly without ranking or weighting actions. This would
separate protocol acceptance from factual-evidence acceptance while leaving
strategic selection to the model. Design the optional evidence schema and
bounded retry/audit behavior explicitly, preserving the old command protocol,
default requests, tool availability and inference guards. First prove frozen
response validation and output headroom; only then consider a short native
trial with strict replay. This is a proposed next design, not an implemented
guard or evidence of eventual mission completion.
