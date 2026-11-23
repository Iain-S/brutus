# Campaign Planner Results

Updated: 2026-11-23. Latest model experiment: 2026-11-23.
Channel-diagnostic source: `4f9682f1`;
Thinking-check source: `747ae57e`; frozen-order source: `56519054`;
compound-model source: `03089798`;
native-preview foundation: `3ce633ac`;
earlier single-macro model checkpoint: `936cc933`.

## Objective And Current Approach

Find fast native wins in peaceful campaign missions, starting with Tarraco
(campaign rank 3, zero-based), without changing game rules, capping population,
or prescribing a human-selected winning build order.

The current experiment uses a local LLM to choose among legal macro actions.
Deterministic code constructs and validates those actions, simulates native
forecasts, executes accepted choices, and records results. It is not a trained
DNN reinforcement-learning policy. The model is
`qwen3:4b-instruct-2507-q4_K_M`, served locally through Ollama.

**No campaign win or demonstrated fast-win strategy has been achieved.**
See [remaining work](PLANNER_TODO.md) for the next checkpoint.

## Latest Follow-up: ToolOutput Choices Change With Presentation

The instruct ToolOutput follow-up completes **eight accepted calls/eight received
responses**, with no retry, timeout, malformed tool arguments or native action.
Three cyclic orders are tested on each of the same two frozen comparisons,
then original-order requests are repeated exactly. Each alternative occupies
every position once per state in the six-call balanced block. The three reverse
orders from the earlier fourteen-call diagnostic are not tested here.

| Comparison Row And Output Enum Order | ToolOutput Decision 2 | ToolOutput Decision 3 | Historical ID-only Decision 2 | Historical ID-only Decision 3 |
| --- | --- | --- | --- | --- |
| compound, single, wait | compound | compound | compound | compound |
| single, wait, compound | single | wait | wait | wait |
| wait, compound, single | wait | wait | wait | wait |
| Exact original-order repeat | compound | compound | compound | compound |

**Both exact repeats agree. Both states change choices across presentations.**
Decision 2 selects all three alternatives; decision 3 selects compound or wait.
Five of the six balanced choices match their corresponding historical ID-only
choices. Single is selected once here, compared with none in that matched old
subset. Five choices occupy the first position and one the second, so this is
not an always-pick-first rule. The two repeats are excluded from those counts.

All native facts, labels and system instructions are unchanged. Row and enum
order change together, so their effects are not isolated. The model/digest,
sampling and seed are pinned; ToolOutput adds chat formatting and a tool schema
through the compatibility endpoint. Historical answers are not fresh interleaved
controls. These targeted states, one seed and three orders cannot establish a
general library effect or optimality. Repeat agreement supports the observed
presentation sensitivity without proving universal determinism.

For example, decision 2's compound and single forecasts both report population
49, fountain coverage 49 and zero food/culture/prosperity, with treasury 7499
versus 7516. Waiting forecasts population 45 and treasury 7566. Which plan is
chosen changes with presentation; no reason for the choice is verified. These
are historical native predictions, not new delivered outcomes, and differences
in future capacity prevent declaring global dominance from named endpoints alone.

Evidence:
`runs/planner-input-probes/2026-11-23/20261123T145332.122978Z_tooloutput-order_d6cf7852/`.
The independent audit verifies all raw/typed outputs, complete usage/finish
telemetry, dynamic schemas, pinned reference/helper/source snapshots, actual
request bodies and byte-identical repeated controls. Original model/default
identity is unchanged and the temporary alias is confirmed removed. There are
zero game ticks, executed choices, proposal calls, saves or screenshots.

Input counts are 5816 or 6002 tokens; every completion is 28 tokens. Worker wall
times, including imports, range 46.1..67.0 seconds and total 401.3 seconds; whole
probe time is 424.9 seconds. Cache/runtime differences and the changed protocol
prevent attributing latency differences to Pydantic AI. Eight synthetic scheduled
calls plus three separate rejection checks pass before inference; no production
code or dependency changed, and no new broad training-suite result is claimed.
See [the committed follow-up protocol](superpowers/plans/2026-11-23-tooloutput-order-followup.md).

ToolOutput provides usable schema validation on this run. Selection reliability
and strategic improvement remain unmet gates. The next native planning experiment
should measure broader root previews or appropriate service/rating horizons as
separate questions, retaining presentation sensitivity as an unresolved selector
property and requiring delivered native progress before policy promotion.

## Previous Spike: Pydantic AI ToolOutput

The user-requested throwaway spike uses Pydantic AI slim 2.71.0, Pydantic 2.14.4,
OpenAI SDK 3.57.0 and httpx2 2.16.2 in an ignored temporary environment. Its
`pip check` passes; the canonical training environment remains unchanged.
Four mock HTTP cases accept valid tool arguments and reject thinking-only
output, an invented candidate and extra fields, with one request each and no
retry. These are mock checks, not four additional model calls.

The real instruct control **passes**. On frozen decision 3 it returns one
`select_candidate` tool call with exactly `decision_id=3` and
`candidate_id=compound`. The raw arguments pass the existing selection validator
and match Pydantic AI's typed result. Usage is 5816 prompt tokens and 28
completion tokens; total worker wall time is 128.8 seconds, including imports.
No thinking text is promoted to an answer. The thinking request then receives
HTTP 400 before generation: this installed Thinking-2507 model rejects
`reasoning_effort=medium`. That failed request remains failed.

Initial two-call archive:
`runs/planner-input-probes/2026-11-23/20261123T083010.246508Z_pydantic-tooloutput_af7ddb97/`.
Its retained independent audit verifies two requests/two received responses,
one accepted typed result, unchanged native facts, model identity and alias
settings. A separate compatibility follow-up omits the unsupported effort field
and uses the thinking model's default mode, with one request maximum and the
same 1536-token/170-second limits. Its outcome is recorded below.

The corrected single-call follow-up **times out after 170.0 seconds**, with no
HTTP receipt or raw response body. The worker is killed; its last in-flight
record is retained alongside the parent's deadline marker and terminal stopped
manifest. There is no accepted thinking result, and no evidence of its token use
or eventual completion. Follow-up archive:
`runs/planner-input-probes/2026-11-23/20261123T083421.127626Z_pydantic-tooloutput_c4fcfe68/`.
Its retained independent audit verifies the omitted effort field, exact tool
schema/native facts, one request/zero responses, deadline and unchanged identity.
Across the real spike and follow-up there are **three request attempts, two
received responses, one accepted instruct result, one HTTP 400 and one timeout**.
There are no automatic retries or further follow-ups.

### Protocol And Interpretation

Pydantic AI exposes exactly one output tool and forbids extra fields. Both the
agent and SDK have retries disabled, a one-request usage limit, a transport guard
against second requests and a killable 170-second worker. All native alternatives,
their original order and the frozen system/prompt are retained. The chat endpoint,
tool schema and reasoning controls differ from previous generate requests; this
is protocol feasibility, not an isolated library effect or strategy comparison.

Ollama 0.16.2's compatibility endpoint cannot set context, top_k or min_p per
request. Unique temporary aliases reuse the exact installed weight blobs and
templates with only num_ctx=8192, top_k=20 and min_p=0 overrides. The instruct
request uses effort=none. The server does not enforce the client's tool-choice
request; returned arguments are validated independently. Do not claim schema
compliance is guaranteed by the decoder. Pydantic AI's successful typed result
shows a usable integration path for instruct, not improved strategic judgment
or reliable thinking-model completion.

All temporary aliases are confirmed absent afterward through `/api/tags`, and
the original model digests remain unchanged. The throwaway cleanup code logs a
JSON parse error for successful empty-body DELETE responses; the independent
tag check verifies actual removal. A separate earlier setup record has zero
inference attempts: the initial alias guard rejected the expected parent-model
metadata before a local regression corrected that check. Neither setup nor
cleanup quirks are model-output failures or grounds to rewrite failed records.

Recommendation: Pydantic AI is a plausible replacement for handwritten typed
output plumbing on the working instruct profile. Before integration, compare
that protocol on balanced frozen presentations and repeated controls while
preserving raw audit evidence. This single successful call cannot establish
selection reliability, a latency improvement, or improved native strategy. Do
not migrate the live planner or treat the thinking problem as fixed from this
spike. The existing validation already prevented malformed output from executing.

The throwaway runner `runs/pydantic_tooloutput_spike.py`, copied source/hashes,
dependency versions, original pinned native reference, wire requests, raw
responses and Pydantic messages/results remain local. No production command or
training dependency is changed. No game actions or saves are produced. See
[the spike plan](superpowers/plans/2026-11-23-pydantic-tooloutput-spike.md).

## Previous Diagnostic: Removing Schema Hits The Deadline

The separate channel diagnostic varies only provider `format` presence on frozen
decision 3. Model/digest, thinking mode, original comparison order, native facts,
system/prompt, seed, sampling, 8192 context, 1536-token cap and 170-second hard
deadline remain fixed. Client-side validation still requires exact final-channel
JSON. The predeclared schedule is schema/omitted/omitted/schema, with transport
or deadline failure stopping remaining conditions.

Only **two attempts and one received response** occur before the stop:

| Condition | Observed result | Elapsed |
| --- | --- | --- |
| Schema present | Complete stop, 19 generated tokens; empty final response, 50 characters of answer-shaped thinking; rejected | 73.5 s |
| Schema omitted | Process deadline; no saved HTTP response or final body; rejected | 170.0 s |

The repeated controls are **not run**. There are no accepted final answers,
retries, increased budgets, game actions or new saves. Whole diagnostic time is
260.3 seconds. No token usage, reasoning content or completion state can be
inferred for the timed-out request from the absent response. Its counter records
one attempted call and zero received responses, not proof of no server work.

The schema control reproduces the prior wrong-channel failure, but omitting the
schema does not establish a usable completion under these bounds. The incomplete
ABBA experiment cannot establish a causal schema effect or repeatability of the
omitted-schema condition. Model quality and strategic improvement are unassessed.
The previous failed capability archive remains unchanged.

Evidence:
`runs/planner-input-probes/2026-11-23/20261123T072451.276953Z_thinking-channel_2e8774df/`.
The retained independent audit verifies exact request intervention, committed
source bytes, original native reference, stable model/default metadata, strict
raw output and both terminal attempt records. Evidence integrity passes; the
experiment status is stopped and complete-schedule acceptance remains unset.
All **214 unittest cases pass**, including five new intervention/lifecycle tests;
fresh source review finds no material issues. See
[the diagnostic plan](superpowers/plans/2026-11-23-thinking-channel-diagnostic.md).

This thinking profile is not ready for a balanced selection-quality comparison
under current operational limits. The next useful direction is a separately
bounded selection-mechanism comparison using the working instruct profile,
keeping all native alternatives available and testing consistency rather than
putting a desired choice first. Larger budgets or another model would be new
experiments, not repairs or retroactive acceptance of these records.

## Previous Diagnostic: Thinking Canary Has No Final Answer

The bounded installed-profile check stops after **three calls and three HTTP
responses: two accepted instruct controls and one rejected thinking canary**.
Both instruct controls reproduce the historical original-order compound choices
on saved decisions 2 and 3. There are no retries, native actions or new saves.

The installed `qwen3:4b-thinking` canary returns HTTP 200, complete generation
and stop telemetry after 19 generated tokens, taking 72.1 seconds. Its final
`response` field is empty. The separate `thinking` field contains 50 characters
of answer-shaped JSON with `candidate_id` and `decision_id` keys. That field is
unverified output, never accepted as the final answer or executed. Strict final
JSON parsing correctly rejects the empty response. Neither the 1536-token cap
nor the 170-second deadline was exhausted; context headroom remains valid.

The conditional fourteen-call thinking sweep and repeat controls are **not run**.
Selection reliability and model quality remain unassessed for this profile.
Weights, template, thinking mode and token allowance differ from instruct, so
this also cannot isolate a thinking effect. A schema/template/channel interaction
is a hypothesis requiring a separate controlled diagnostic, not an established
cause. Increasing the generation budget does not address this observed failure.

The original metadata guard also reports a change because `/api/show` reorders
parameter groups and generated Modelfile parameter lines. Independent audit
finds unchanged digests, templates and effective defaults. The archived run
remains failed, including its withdrawn identity and success gates; observed
control agreement is not a retrospective promotion of those gates. A regression
fix for future runs compares parameter groups by name, preserving actual values
and repeated-value order, and retains the original raw metadata. No inference
is repeated after this fix.

Evidence:
`runs/planner-input-probes/2026-11-22/20261122T214852.589224Z_thinking-capability_0f329319/`.
Its retained `independent-audit.json` and audit source verify the failed record,
three receipts, reference/source integrity, wrong-channel output and metadata
presentation diagnosis. All **209 unittest cases pass**, including regressions
for parameter-order normalization and rejecting answer-shaped thinking as a final
answer. Generated evidence remains local. See
[the check plan](superpowers/plans/2026-11-22-thinking-selection-capability.md).

## Previous Diagnostic: Frozen Choices Change With Presentation

Input-only archive:
`runs/planner-input-probes/2026-11-22/20261122T151628.185019Z_compound-order_4af8da6b/`.
This uses only saved decisions 2 and 3 from the native compound run below.
There are **zero new game ticks, executed choices, proposal/query calls, saves
or screenshots**. Historical native forecasts remain predictions from that
source; they are not relabelled as delivered outcomes of this diagnostic.

Each state receives all six permutations of the same three native comparison
rows and response enum, followed by a byte-identical repeat of the original
order. State order alternates within adjacent pairs. Every alternative occupies
every position twice in the twelve-call balanced block. Seed 20261122 is added
to every request in this separate profile; other sampling/model/digest/context
and token/deadline settings remain unchanged. Historical unseeded answers are
not paired controls. Labels and system instructions stay fixed.

All fourteen calls pass inference, schema, headroom, HTTP, deadline, immutable
source and audit checks, with no retries or fallback. **Both exact repeated
controls reproduce their first choice.** Nevertheless, each frozen state changes
between compound and wait under different presentations of unchanged facts.

| Comparison Row And Schema Order | Decision 2 Choice | Decision 3 Choice |
| --- | --- | --- |
| compound, single, wait | compound | compound |
| single, wait, compound | wait | wait |
| wait, compound, single | wait | wait |
| compound, wait, single | compound | wait |
| wait, single, compound | wait | wait |
| single, compound, wait | wait | wait |
| Original-order repeat (separate controls) | compound | compound |

In the balanced block, decision 2 selects compound twice and wait four times;
decision 3 selects compound once and wait five times. Single is never selected.
Seven choices occupy the first position, three the second and two the third:
this is not a literal always-pick-first rule. The two repeated controls are
excluded from these balanced counts.

On decision 3, compound and wait report the same population (49), food, ratings,
fountain coverage, blocked-house count and maximum housing level, but treasury
7443 versus 7473. Presentation changes which is selected. Other diagnostic or
future-capacity effects can differ; this is not a proof of global strategic
dominance. On decision 2, compound forecasts population 49 versus wait's 45,
with treasury 7499 versus 7566: presentation also changes that explicit
population/finance tradeoff. No weighted strategy score is introduced.

### Interpretation And Evidence

The current fixed-seed selector is sensitive to combined row/schema presentation
on these two states. Do not treat a single accepted response as evidence of a
stable strategic preference, or fix the policy by placing a desired answer
first. The intervention does not separate visible row order from schema enum
order; fixed system-label order, one seed, two targeted states, and uncontrolled
cache/runtime behavior limit generalization. The matching repeats support the
observed sensitivity but do not prove determinism for every future request.
Root selection, search breadth, horizon and model capability remain unisolated.
There is no new campaign result or demonstrated fast-win strategy.

Input counts are 5680..5866 tokens and all outputs are 15 tokens. Calls take
22.2..52.5 seconds, 445.7 seconds total; whole probe time is 452.4 seconds.
Ollama version is recorded as 0.16.2. The archive pins the exact old manifest,
requests, raw responses and accepted audits, and copies the original records and
source so the historical inputs can be audited without the original directory.

`independent-audit.json` and its retained audit source verify every allowed
transformation, preserved value/type, exact schedule, strict raw response,
accepted answer, call count, source hash, condition proof and byte-identical
control request. The audit makes no model calls or native actions. All 193
unittest cases pass, including eleven new order/provenance/lifecycle tests.
Existing live command behavior and historical evidence are unchanged. See
[the diagnostic plan](superpowers/plans/2026-11-22-compound-order-diagnostic.md).

### Native Timescales Before Further Campaign Evaluation

Source inspection establishes 50 ticks/day, 16 days/month and 12 months/year:
800 ticks/month and 9600/year. Actual prosperity and peace update on annual
rollover. From zero peace and zero peace-years, an illustrative clean sequence
is 2, 4, 9, 14, 19, 24, 29, 34 across eight annual updates; crime, riots and
destruction can reduce progress. This is not a guaranteed trajectory. The native
eight-month prefix cannot assess annual rating progression. See
[calendar code](../src/game/time.c), [update dispatch](../src/game/tick.c) and
[ratings](../src/city/ratings.c).

Farm production instead requires labor coverage and workers, advancing daily
worker-based work toward 200 raw-resource points, with an extra eligible
non-northern wheat update. There is no annual harvest gate in that production
path. Staffing, carts and delivery still require actual native time; source
inspection does not guarantee delivery within a chosen horizon. The source
policy never built a farm, so its zero food should not be excused solely as an
annual-harvest delay. See [industry code](../src/building/industry.c).

## Latest Native Model Run: Verified Compound Execution, No Strategic Fix

Run directory, relative to the checkout:
`runs/tarraco/2026-11-22/20261122T101738.483176Z_compound-model_11fb32a7/`.

The separate experimental command makes three model calls per decision: select
a first macro from the whole legal menu, select a continuation from its native
simulated successor menu, then select the compound, the same first macro plus
waiting, or waiting alone. All final alternatives last 1600 native ticks. One
root and one continuation are proposed per decision; this is not broad tree
search or a comparison with an independently optimized single-step policy.

All twelve calls pass exact schema, model identity, native provenance, complete
inference, token/headroom and deadline checks. Four decisions deliver 6400 actual
ticks with no retries, repairs, fallback, validation failure or timeout. The
pinned model/digest and .7/.8/20/0 sampling are unchanged. Input sizes are
2581..5866 tokens, outputs 15..34; calls take 46.6..68.3 seconds, 730.7 seconds
total. The whole model run takes 988.2 seconds, including native previews and
execution. It stops at the decision budget, not victory or episode truncation.

| Decision | Model-Proposed First / Second Macro | Selected Execution | End Population | Fountain Residents | Treasury |
| --- | --- | --- | --- | --- | --- |
| 0 | Housing / Water supply | Both | 42 | 42 | 7,708 |
| 1 | Landscaping / Market | Both | 52 | 52 | 7,592 |
| 2 | Landscaping / Water supply | Both | 49 | 49 | 7,499 |
| 3 | Water supply / Water supply | First, then wait | 49 | 49 | 7,458 |

The final city has health 50, favor 50, personal savings 64, maximum housing
level 1 and native cached prosperity cap 10. Actual prosperity, culture and peace
remain zero. Food stocks, granary/market inventory, household food delivery, farm
workers, tax coverage and collected tax denarii remain zero. No farm or cultural
service is selected. The complete wheat-supply macro is legal in all eight
proposal menus; cultural services are legal in seven (all after the initial
empty-city menu). A market is food-related, so this is not evidence that the
model ignored every food tool.

### What The Equal-Time Comparisons Establish

- At decision 0, housing plus water delivers 42 fountain-covered residents;
  housing alone forecasts the same population with no fountain coverage.
- At decision 1, landscaping plus market delivers population 52, compared with
  forecast 48 for landscaping alone and 44 for waiting. This is a local native
  endpoint difference, not evidence of sustained food delivery or campaign wins.
- At decision 2, the selected compound forecasts the same population, fountain
  coverage, blocked-house count, housing level, food and ratings as its single
  control, but 17 fewer treasury denarii. Other diagnostics/future capacity can
  differ; no general optimality claim or weighted score is assigned.
- At decision 3, the model declines its second water build, retaining 15 more
  denarii than the compound. Waiting alone forecasts another 15 denarii with the
  same population, food, coverage, blocked-house count, level and ratings. The
  ID-only answer does not establish the model's reasoning for its choice.

The final menus report equivalent action-trace groups explicitly; none of this
run's alternatives has an identical action trace. Three compound selections and
one single selection therefore demonstrate working selection access, not a
strategic advantage of planning depth. Final menu order is fixed, sampling is
unseeded, and there is only one sequential run. Root selection, limited search
breadth, horizon, model capability and presentation effects are not isolated.
Compared with earlier single-macro experiments, protocol and decision cadence
also differ. **Better campaign play remains unproven.** Do not extend this policy
unchanged and describe it as a fast-win strategy.

### Audit And Replay

Every accepted proposal matches its original raw model response. Both preview
prefixes match the actions, full native scalars and six diagnostics of the exact
successor shown to the model. Every selected macro is regenerated and validated
again in the actual successor. All four actual traces and stage/final endpoints
match their forecasts. `independent-protocol-audit.json` and its retained audit
source independently reconstruct requests, schemas, choices, provenance, API
accounting, source hashes, actual trace and final artifacts from the archive.
This audit makes no new model calls or native actions.

Fresh-process strict native replay matches all 6400 messages/rewards, population,
victory state and all six final diagnostic payloads:
`runs/tarraco/2026-11-22/20261122T103511.549786Z_replay_081a68e5/`.
The source archive retains its actual `final.sav`, six diagnostics, per-decision
requests/raw bodies/HTTP status, full successor/proposal/preview/comparison/actual
payloads, before/after model digests and source/library hashes. Screenshot capture
is still manual/pending; no `final.png` has been fabricated.

Source verification passes all 182 unittest cases (40 compound-related), native
forecast health and previous rollback controls. A fixture-only orchestration
control also passes independent replay; it is labelled separately and contributes
zero model calls to this experiment. Source-review findings about prefix binding,
real process deadlines, completion telemetry and damaged-audit finalization are
fixed with regression coverage. See
[the experiment plan](superpowers/plans/2026-11-22-compound-model-evaluation.md).

## Native Compound Preview Checkpoint: 2026-11-21

An additive `julius_gym.compound` interface now previews one or two named macro
steps, regenerating native-tested legal candidates in each successor state.
Plans carry no future candidate objects or action arrays. Initial state and
native observation freshness are checked; unavailable successors, construction
failures, terminal outcomes and exhausted budgets stop the plan immediately.
Construction and observation ticks share the actual remaining budget.

An outer snapshot restores the base on success, invalid successor or exception.
Each preview includes a wait control from that same base for the plan's actual
charged ticks. `plan.valid` and `equal_time` are separate gates: an invalid prefix
is not a valid plan and a control that ends early cannot support an equal-time
comparison. Raw per-stage actions, messages, rewards, tick counts, net treasury
changes, full scalar observations (including peace), staffing/food diagnostics
and all six final native diagnostic payloads are retained.

The following are fixed engineering fixtures, **not model proposals or strategy
evidence**. Both completed plans ran for 1,600 ticks, including an 800-tick
minimum cycle per step. The invalid plan stopped at 800 ticks; each wait control
used exactly its corresponding duration.

| Fixture | Status | Population | Fountain Residents | Treasury | Food / Culture |
| --- | --- | --- | --- | --- | --- |
| Housing, then successor water supply | completed | 42 | 42 | 7,708 | 0 / 0 |
| Wheat supply, then successor school | completed | 24 | 0 | 7,182 | 0 / 0 |
| Housing, then nonexistent successor | invalid_successor | 13 | 0 | 7,818 | 0 / 0 |
| Wait control, 1,600 ticks | completed | 0 | 0 | 7,984 | 0 / 0 |
| Wait control, 800 ticks | completed | 0 | 0 | 7,992 | 0 / 0 |

The wheat/school fixture still has zero farm workers, food inventory, food
delivery and culture at this horizon. Successful construction is not successful
staffing or service delivery. No native victory or strategic improvement is
claimed, and the live model command has not changed.

All corrected previews restore the native fingerprint, freshly read native
scalars and all six diagnostics. The plan's raw-action continuation then runs
directly from the restored base, without resetting or regenerating candidates;
this checks hidden-state rollback effects. Stage endpoints and final diagnostics
match predictions. Separate fresh-process `examples/replay_run.py` invocations
also match every action message/reward and all six final diagnostics for all six
archives. That is 8,000 independently replayed ticks across controls and prefixes.

Source-pinned evidence under `runs/tarraco/2026-11-21/`:

- Housing/water: `20261121T183154.823269Z_compound-control_d63f5bba/`;
  wait: `20261121T183155.415341Z_compound-control_a7c75678/`.
- Wheat/school: `20261121T183204.879826Z_compound-control_f3511cb6/`;
  wait: `20261121T183205.438715Z_compound-control_0caf8df1/`.
- Invalid successor prefix: `20261121T183215.374656Z_compound-control_925d4b0b/`;
  wait: `20261121T183215.731156Z_compound-control_a8f76d93/`.

Each archive contains `preview.json`, source snapshots/source and library hashes,
the actual trace, real `final.sav`, six final diagnostics, `REVIEW.md` and
`independent-replay.log`. Earlier dirty-source controls are retained as preliminary
evidence; the directories above pin committed source `3ce633ac`.

All 161 unittest cases pass, including 19 compound cases, 110 planner cases and
seven replay cases. Native forecast health and the compound controls pass;
`python -m pip check` reports no broken requirements. Full wildcard unittest
discovery was also attempted: seven existing CLI scripts fail importing without
their required path arguments and `test_import` fails printing Unicode under
Windows cp1252. The complete set of actual unittest-class modules passes. Exact
script names and fresh-review corrections are in
[the implementation plan](superpowers/plans/2026-11-21-compound-previews.md).

## Previous Single-Macro Native Run: 2026-11-19

Run directory, relative to the checkout:
`runs/tarraco/2026-11-19/20261119T105542.706780Z_planner-local_d54f5084/`.

- Eight accepted decisions, 6,400 native ticks, sixteen API calls.
- No retries, fallbacks, timeouts, or validation failures.
- Selected two housing expansions, three markets, one water-supply macro,
  and two landscaping macros.
- End state: population 56, fountain coverage 42 residents, health 50,
  treasury 7,234, favor 50.
- Culture, prosperity, peace, food stocks, food delivery, and tax income
  remained zero; maximum occupied housing level was 1.
- Stopped at the decision budget, not at a native victory.

Independent strict replay matched all 6,400 action messages and rewards and
all six final diagnostic payloads:
`runs/tarraco/2026-11-19/20261119T110723.972040Z_replay_a909eb19/`.
The full-prefix review and native save are in
`runs/tarraco/2026-11-19/20261119T110726.136443Z_planner-prefix-review_0a31f0cf/`.

The complete wheat-supply macro was legal at every decision but never queried.
Cultural-service macros were legal from decision 1 but never queried. Markets
are food-related, so this does not mean the model ignored every food tool.
These observations motivated the frozen full-domain experiment below.

## Latest Frozen Experiment

The final selection stage was allowed to choose any currently legal candidate,
not only candidates in its earlier two-item query. Four saved states were
tested under narrow and full-domain profiles, twice each: sixteen final API
calls, no new query calls, and no game actions.

| Saved Decision | Original Query | Narrow Choice, Both Repeats | Full Choice, Both Repeats |
| --- | --- | --- | --- |
| 1 | Water, Market | Market | Water |
| 3 | Water, Granary | Water | Water |
| 5 | Water, Market | Market | Water |
| 7 | Housing, Farmland | Housing | Housing |

All sixteen responses passed validation. None of the eight full-domain
responses selected an action outside its original query. Broader final access
works technically, but did not demonstrate broader exploration or better play.
This is a small, unseeded, frozen-context experiment, not a strategy benchmark
or a causal isolation of model capability, lookup anchoring, or planning depth.

Evidence:
`runs/planner-input-probes/2026-11-19/20261119T173520.971552Z_full-domain_ab0ae6bc/`.
Detailed protocol, audits, limits, and source validation are recorded in
[the completed experiment plan](superpowers/plans/2026-11-19-full-domain-selection.md).
The full-domain helpers have not been promoted into the live command.

## Verification And Limits

- The completed checkpoint records 110 planner tests and seven replay tests
  passing, plus independent source review. These are historical results, not
  a claim that tests were rerun for this documentation update.
- Native water-allocation cursor rollback was repaired and tested earlier;
  the latest native trial passes strict replay. This is not proof of
  determinism for every future compound rollout or multi-year campaign.
- Earlier failed evidence-quoting and timeout experiments remain failed gates;
  successful ID-only selection does not retroactively validate them.
- Tarraco targets population 2,500, culture 45, prosperity 25, peace 30,
  and favor 70. The 6,400-tick prefix cannot establish a win. Peace progression
  alone requires multiple annual updates under native rules.
- Native housing level 4 contributes prosperity 25 without requiring pottery.
  Missing industrial macros therefore do not by themselves prove that the
  prosperity target is unreachable. Actual staffing, food, evolution,
  finances, and annual ratings still need to be demonstrated.
- Native multi-step previews and a bounded model-proposed compound experiment
  are now verified as described above; neither establishes strategic improvement.

## Artifacts And Manual Review

Native campaign runs use
`runs/tarraco/YYYY-MM-DD/<UTC>_<mode>_<uuid8>/`, containing `run.json`,
`actions.jsonl`, real `final.sav`, six final diagnostics, and `REVIEW.md`.
Input-only model probes and command transcripts have separate directories.
Generated artifacts are local and ignored; repository documents retain their
paths so they can be located without committing game assets or run output.

Real-asset `final.png` review remains manual/pending using graphical Julius
and its screenshot facility. No automatically rendered in-game screenshot
has been established by these experiments.
