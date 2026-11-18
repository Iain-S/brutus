# Frozen Planner Factual Grounding Diagnostic Plan

**Goal:** Determine whether the current local model can recover recorded game
facts before changing its action-selection policy. Continue the diagnostic
checkpoint accepted after `1fcdd0ad`; this is not a production planner feature.

**Scope:** Read-only model probes on decisions 5 and 7 from the verified
November 18 `planner-local_03ba650f`. No Gym environment, DLL load, game actions,
new native state or copied save. Keep all candidates, scalar values/types,
mission objective and game facts. Preserve staged models and historical runs.
Use the current authorized branch, canonical interpreter and installed pinned
instruct model. No server settings, model installation or gameplay changes.

## Hypotheses And Alternatives

The live explanations claim housing is absent in a populated city, inflate a
72-tick action to 782 ticks and describe more blocked houses as an improvement.
These could reflect difficulty reading positional candidate rows, difficulty
reconstructing baseline overrides, arithmetic errors, or explanations that do
not faithfully represent action selection. A greedy but factually competent
policy is also possible. Do not assume a particular explanation in advance.

Compare production positional candidate rows against explicitly named
candidate fields, keeping the existing absolute forecast overrides and actual
wait baseline in both. This isolates outer row labelling, not every aspect of
encoding. Full independent forecast objects would substantially enlarge the
input and confound the test with context capacity; changing model or strategic
instructions now would confound representation with policy.

## Protocol

- [x] Verify model digest, source manifest and source-context identity. Build a
  throwaway ignored diagnostic script, not a deployed adapter option. Check
  exact conversion roundtrips, every candidate/order/nonforecast field, all
  twenty scalar projection values/types and independent factual oracles.
- [x] Run two repetitions for each state and each layout (eight calls), with
  the same 8K context, 256-token output, existing instruct sampling and
  170-second API timeout. Alternate layout order within each state. No hidden
  retries, candidate selection, answer hints, rankings or game actions.
  Retain full requests/responses, token counts, termination details and errors.
- [x] Score twelve integer factual answers exactly, including current
  population, housing/wheat construction durations, forecast duration,
  housing/wait/wheat projected populations, housing/wait blocked-house counts,
  wheat food stock and two housing-minus-wait differences. Expected answers
  come independently from the recorded native context, never from model text.
  No correct-value enums or expected answers enter the requests. Require
  complete exact-key/type responses and existing inference/headroom checks.
- [x] Report extraction versus arithmetic errors separately, per layout/state
  and repetition; audit failures separately from wrong answers. State the
  limits of targeted tasks, two repetitions, stochastic sampling and changed
  output schema. A successful factual audit does not validate free-text
  explanations, action choices or a mission win. Review evidence, record the
  next checkpoint and commit/push source documentation only.

## Artifacts And Acceptance

Use `runs/planner-input-probes/YYYY-MM-DD/<UTC>_grounding_<uuid8>/` with
`native_execution: false`, `executed_choices: 0`, source-run/save references,
source hashes, requests, raw responses, per-call scores and an aggregate audit.
Do not fabricate a fresh `final.sav` or claim a screenshot/replay for this
input-only experiment; its source campaign already has a strict replay.
Use type-aware equality (booleans are not integer answers), explicit schema
checks and no numerical tolerance. Any rejected/truncated request is not an
accepted factual answer. Preserve failure evidence and do not relax guards.

The user has delegated continued investigation and requested this next
checkpoint. This small diagnostic uses the existing probe pattern; it does
not authorize deploying named candidates, changing planner defaults, adding
human build orders or promoting a profile. Implementation choices above are
the investigator's, not claimed as user-prescribed strategy.

## Completed Input-Only Diagnostic

On protocol commit `de492e8b`, diagnostic folder
`runs/planner-input-probes/2026-11-18/20261118T134211.990557Z_grounding_64250d06/`
contains all eight full requests/responses, two copied source contexts,
`metadata.json` and independently recomputed `evaluation-audit.json`. No new
native state, save, simulation, choice or replay was produced. Source context
and manifest hashes, script/adapter hashes, pinned model digest and the prior
verified campaign save/replay reference are retained. The source trace's end
save is not misrepresented as the intermediate decision-5 native state.

All eight calls completed normally with `done_reason: stop`, passed the
existing inference/headroom guard and returned exact integer response schemas.
There were no retries, inference failures, timeouts or length-limited outputs.
Here, accepted means valid transport/schema, not correct factual answers.
Production adapter bytes/defaults and all game behavior are unchanged.

Before inference, self-checks verify lossless row conversion, all 20 scalar
values/types, source identity and the independent oracle. The scorer rejects
bool/float/string/null, missing/extra fields and duplicate JSON keys, and
distinguishes injected extraction and arithmetic mistakes. A separate post-hoc
audit rebuilds the oracle directly from the source trace, compares saved
responses/scores and checks request-pair equality except candidate layout.
All 61 focused planner and seven replay unit tests also pass today; those
tests do not turn this input-only diagnostic into a new native execution test.

| Frozen Decision | Layout | Correct Facts In Each Repetition | Input Tokens | Output Tokens |
| --- | --- | --- | ---: | ---: |
| 5: Population 193, 53 Candidates | Table | 11/12, 11/12 | 6,025 | 125 |
| 5: Population 193, 53 Candidates | Named | 10/12, 10/12 | 7,322 | 124 |
| 7: Population 245, 47 Candidates | Table | 12/12, 12/12 | 5,798 | 126 |
| 7: Population 245, 47 Candidates | Named | 10/12, 10/12 | 6,945 | 126 |

Table totals are 46/48 facts, with two completely correct responses out of
four. Named totals are 40/48, with no completely correct responses. Inference
took about 769 seconds overall, including cold loading; this is not an
isolated throughput benchmark. Answers repeat identically within each
state/layout pair despite the configured stochastic sampling. Two repeats do
not provide independent statistical evidence or establish a general ranking
of layouts/models. Both layouts retain required context headroom, but naming
fields costs additional input tokens and is not a proven fix here.

### What Failed And What Did Not

All current-population, projected-population, food-stock and blocked-house
questions are correct. All sixteen requested arithmetic differences are
correct, including positive blocked-house changes of +5 and +7. Neither
layout reproduces the free-text assertion that housing is absent. Wheat
construction duration is correctly read as 55 and 72 in all eight responses,
despite the earlier action-selection explanation calling the latter 782.

Errors are confined to duration fields in this targeted task. Both table
answers at decision 5 report housing construction as 800 rather than 25 ticks;
table decision 7 reads its 20 ticks correctly. Every named response instead
reports housing construction and forecast duration as 800, where construction
is 25/20 and the forecast is 1,600. The execution cadence and recent outcome
durations are 800, but the experiment does not establish which occurrence
caused the incorrect answer. It is evidence consistent with duration-scope
confusion, not proof of its mechanism or the cause of housing-only play.

Correct reconstruction and arithmetic in explicit questions do not prove
correct use during action selection or faithful free-text explanations. This
test changes the output task/schema and is targeted to two known problematic
states. No model action is selected, so no policy or mission improvement is
measured. Do not promote named candidates or add strategic scoring from this
result; the production adapter stays unchanged.

### Next Checkpoint

Test unambiguous duration scopes as a minimal frozen-state diagnostic:
explicitly distinguish candidate construction ticks, forecast ticks and
recent charged execution ticks while retaining every value, candidate and
objective. Compare against the existing table, not the worse named variant.
If factual duration extraction improves, separately probe the original
choice task without executing its answer to check transfer; extraction alone
is not sufficient. Keep all failures visible and do not turn the exercise
into a prescribed action sequence, weighted strategy or hidden tool filter.
If action selection still ignores correctly read multi-goal forecasts,
investigate planning depth or machine-checked factual comparisons separately
rather than assuming more field labels solve strategy.
