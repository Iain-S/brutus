# Local model planner

`run_planner.py` runs a decision loop over a small macro vocabulary. It does not
require the scripted controller to win first. This is an initial planner interface,
not a demonstrated LLM solution to Tarraco.

The compact local request preserves the explicit objective: win in minimum
simulation ticks. Treasury is relevant to feasibility, not a replacement
optimization target. The candidate vocabulary now includes basic education and
entertainment, but complete mission reachability is not demonstrated. Successful
construction, a higher population or one satisfied rating is not a win.

Every invocation automatically retains a persistent end save and run manifest;
see [RUNS.md](RUNS.md) for the naming convention and manual Julius PNG capture.

## Run

Use the dedicated training environment, original game data, and rebuilt library.
From `python/`, test execution without a model:

```shell
python examples/run_planner.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH> --max-ticks 1600 --max-decisions 4
```

This explicitly reports `rule-smoke` mode: it builds one settlement and waits.
It is not evidence of LLM decision-making.

To connect a local command, supply a JSON argv array. The command reads one JSON
state summary from stdin and must write only its JSON decision to stdout. It runs
in the launch directory, with a default 60-second timeout (`--model-timeout`
accepts 1..300 seconds per attempt). Use absolute paths for adapters
and model files. No shell is used. For an already installed Ollama model:

```powershell
$modelCommand = '["ollama", "run", "<INSTALLED_MODEL_NAME>", "--format", "json", "--hidethinking"]'
python examples/run_planner.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH> --model-command $modelCommand
```

Model installation/download is separate; select an installed model appropriate
to the machine. A slow cold start can exceed the timeout and trigger fallback.
The adapter is provider-independent; Ollama is an example, not a dependency.

## Optional Reason-First Profile

Add `--reason-first` to the `examples/ollama_planner.py` command argv to request
a brief comparison of reported forecasts before selecting the candidate ID.
This is experimental and off by default. It changes only the generic rationale
instruction and JSON property order, not game facts, legal candidates, native
actions, sampling options or the three-field decision contract.

The adapter audits `reason_first: true/false` on stderr, including responses
rejected for insufficient headroom. Reasons are untrusted model text: previous
probes invented numerical benefits. Judge native executed outcomes and strict
replay, not explanation quality. Longer rationales consume the same configured
output budget; exhaustion still fails rather than accepting a partial choice.
No build order, candidate ranking or service-placement policy is imposed.

## Optional Forecast Packing

Add `--forecast-format overrides` to the Ollama adapter command to encode each
forecast as named **absolute values** overriding the actual `wait` projection
in `forecast_baseline.forecast`. Omitted fields equal that baseline, not zero;
null still means unknown. Merge the baseline and a candidate's overrides to
recover all emitted forecast fields, including its own time and status.

The encoding preserves every legal candidate, its order, scalar values/types
and all nonforecast fields. It neither ranks actions nor recommends waiting.
If wait is absent, the baseline has null candidate ID and an empty forecast;
each candidate then contains its full named projection. Disabled forecasts add
no encoding. Existing `rows` (default) and `objects` requests are unchanged.

Packing is independent of `--reason-first` and audited as the selected
`forecast_format`; context/output validation remains enforced. Raw engine
context and normal end-state review artifacts remain in the run bundle.
Fitting one occupied-state prompt does not demonstrate full-mission scalability
or a successful strategy, and model rationales remain unverified.

### Optional Verified Comparisons

Add `--verify-comparisons` to the Ollama adapter command to replace unverified
free-text reasons with checked forecast evidence. It is mutually exclusive
with `--reason-first` and requires forecasts plus an actual wait projection.
It works with rows, objects and overrides; `--forecast-format overrides`
remains useful for input size. Existing defaults and legacy request bytes are
unchanged when the new flag is absent.

The model chooses two distinct legal alternatives (one if only wait exists),
quotes their macro/forecast durations, population, culture, prosperity, food
stock, blocked-house counts and blocked-house differences versus wait, then
selects one of those alternatives. No action ranking, preferred tools or build
order is supplied. Every original candidate remains selectable. Integers and
nulls must match the original context exactly; unknown is not zero. Duplicate
keys, stale IDs, wrong counts/types and incorrect facts reject the entire
response rather than substituting repaired values.

After normal inference/headroom checks and evidence validation, the adapter
returns the SAME three-key command protocol below. Its `reason` contains
adapter-generated JSON with `verified_comparisons`, not a model-written
rationale. Stderr audits `verify_comparisons`, `comparison_validation`, checked
facts on acceptance and a bounded `validation_error` on rejection. An inference
failure leaves comparison validation `not_run`; no rejected choice reaches
stdout. There is no internal retry. The runner still allows two attempts and
then logs wait fallback; its retry input currently contains the generic
command-failure error, not the detailed stderr mismatch.

Matching quotes do not establish optimality, truthful unquoted claims,
coverage beyond the checked fields, or successful future construction. A
forecast is a native continuation without later building decisions, not a
mission-win guarantee. Null matches only unknown data. Evaluate transport,
evidence correctness, fallback behavior and actual game outcomes separately.
The first pinned instruct-model frozen trial rejected all four responses for
incorrect quoted facts, despite completed inference and adequate token budgets.
Do not treat this optional flag as a proven live policy or enable it by default;
see `docs/superpowers/plans/2026-11-18-verified-planner-comparisons.md`.
Test the optional boundary with:

```shell
python -m unittest discover -s . -p 'test_planner_verified_comparisons.py'
```

### Experimental Model-Directed Lookup

`ollama_planner_lookup.py` provides pure request/validation helpers for an
input-only two-stage experiment; it is NOT a runner command or new CLI flag.
Stage 1 presents the full existing compact context and legal candidate set.
The model requests two distinct IDs of its choice (one for a wait-only set).
Stage 2 retains the common context and returns fully expanded native forecasts
for those alternatives and actual wait, explicit comparison facts, native
macro outlay and a full-context SHA-256 provenance record.

The final schema permits only the model's own requested alternatives. A final
choice must quote the same strict evidence fields as `--verify-comparisons`;
the lookup contents/hash and quoted facts are rechecked against the ORIGINAL
context, never trusted merely because they appear in the lookup. The helper
then returns the old three-key command response. Invalid/stale/tampered data
is rejected, not repaired. Existing adapter commands/defaults are unchanged.

Explicit facts supplied before generation are a different interface, not
proof of independent fact reconstruction, strategic understanding or optimal
self-shortlisting. Initial selection can still miss a better alternative.
Two stages also cost two API calls: a future command needs explicit aggregate
timeouts and API-call telemetry, not the runner's command-invocation counter
silently relabelled as model calls. No live integration is provided here.
See `docs/superpowers/plans/2026-11-19-planner-fact-lookup.md` for the bounded
frozen transaction protocol and its separate feasibility gate.
The first four transactions all produced valid lookup requests/native facts,
but the final-choice calls timed out within the 290-second total transaction
budget. Zero final choices were accepted. No completed final responses exist
to assess quote accuracy; this is a latency failure, not evidence of corrected
or incorrect final quotes. No live integration is promoted from these probes.

Separate helpers `lookup_selection_request_body` and
`adapter_owned_lookup_choice` test a smaller final contract: the model returns
only the current `decision_id` and one requested `candidate_id`. The same
native lookup/provenance is checked, but factual evidence is attached by the
adapter with `evidence_origin: adapter`, context hash, requested IDs and native
comparisons. It is NOT labelled as verified model quotes. Extra numeric claims,
comparisons and reasons reject instead of being ignored. Old quote-checking
helpers and default commands are unchanged, and no live CLI is provided.
Matching adapter-owned facts cannot establish that the model understands them
or chooses well. This distinct contract has its own frozen timing gate in
`docs/superpowers/plans/2026-11-19-planner-lookup-selection.md`.
The first frozen ID-only probe completes all four transactions without retry,
rejection or timeout (eight API calls, 62.6..66.8 seconds per transaction).
Native evidence/provenance and both-stage requests are independently audited.
No actions are executed. The unchanged query stage is also much faster than
in the preceding probe, so these timings do not isolate a schema-only benefit.
This is interface feasibility on two frozen states, not model comprehension,
strategy quality, a native trial or a passing result for the older quote gates.

### Bounded Lookup Command

`ollama_lookup_planner.py` is a SEPARATE command for the ID-only interface.
Use its absolute path and the active interpreter in `--model-command`, e.g.:

```json
["<ABSOLUTE_PYTHON>", "<ABSOLUTE_REPO>/python/examples/ollama_lookup_planner.py", "--model", "qwen3:4b-instruct-2507-q4_K_M"]
```

It reads the existing JSON context and returns the same three-key choice only
after lookup, selection, provenance validation and final audit persistence.
Defaults match the frozen probe: 8K context, 256 output tokens, instruct
sampling, `--api-timeout 170` and `--total-timeout 290`. Use an outer runner
`--model-timeout 300` plus enabled forecasts. There is no internal retry or
native action in the command. Old commands, flags and runner fallback policy
are unchanged. Two runner attempts can make up to four API attempts per
decision; runner `model_calls` still means COMMAND invocations, not API calls.

Every invocation archives input, source hashes/snapshots, both requests/raw
responses, native lookup and terminal manifest in
`runs/planner-command-calls/YYYY-MM-DD/<UTC>_lookup_<uuid8>/`. Override the root
with `--audit-root`. Initial stderr provides an audit pointer before inference;
the compact terminal summary includes actual attempted/returned API counts
and stage statuses. Full details belong in that directory, not truncated
stderr. Input fingerprints include per-attempt validation errors, so do not
compare them to a base decision context with those fields omitted.

Raw HTTP bodies are saved as `query.response.body` / `choice.response.body`
before JSON parsing; malformed or duplicate-key payloads remain available.
Returned-response counts mean complete bodies received, not valid JSON or
accepted choices. Prepared requests are separate from transport attempts;
an audit-write failure before transport must not count as an API attempt.
The elapsed per-call acceptance deadline is enforced in addition to socket
and whole-command timeouts, with a hard 170-second per-call maximum.

Wrong queries/selections, unsafe inference, late returns and audit-write
failure produce no choice on stdout. A process kill cannot guarantee terminal
audit finalization; retain the initial pointer/progress and cross-check the
parent attempt's return status and received choice. An audit manifest alone
does not establish native execution or successful receipt. Command artifacts
contain no new native save; normal parent campaign bundles retain those.
If a hard kill leaves only a prepared/running stage, its eventual transport
count can be unknown; do not treat an old progress counter as exact zero.

Adapter-owned evidence verifies the supplied facts, not model comprehension or
strategic quality. Treat a live trial and strict native replay as separate
checks; the previous frozen gates are not retroactively changed.

### Experimental Full-Domain Final Selection

Separate pure helpers `full_domain_lookup_selection_request_body` and
`adapter_owned_full_domain_choice` test broader final access. The complete
original compact menu, forecasts, order and common facts remain visible,
alongside the model-requested lookup. The final two-key response may select
any CURRENT legal candidate, not just a queried one. No action is recommended,
ranked or forced. Old narrow selectors still enforce queried membership;
the live command has no full-domain flag or automatic behavior change.

Evidence explicitly records `selection_domain: all_current_candidates`,
original requested IDs and the selected ID. Native comparisons include the
query IDs plus an unqueried selection once, derived from the raw context.
Provenance/type/identity checks, unknown-null semantics and the reason-size
bound remain. An unqueried selection is not labelled as queried or as a model
quote. Broader access alone is not strategy quality; the paired frozen
protocol is `docs/superpowers/plans/2026-11-19-full-domain-selection.md`.
The first paired final-call probe accepts eight narrow and eight full-domain
responses, but all eight full selections stay inside the recorded query.
Full chooses water six times and housing twice; no game action is executed.
Access/schema feasibility is not strategic improvement or proof that query
membership alone caused the earlier omissions. The full-domain helper remains
experimental with no live flag; the next proposed diagnostic concerns native
multi-step plan consequences, not another claim of better play from formatting.

## Contract

Input contains `decision_id`, victory goals and numeric city state, household
food/water coverage, remaining simulation budget, candidate placements and net
treasury outlay, unavailable macros with reasons, and the previous execution
result. Output must be exactly:

```json
{"decision_id": 0, "candidate_id": "expand_housing", "reason": "Provide capacity for immigration."}
```

Only current candidate IDs are accepted; arbitrary code, extra fields, unknown
actions and stale decisions are rejected. Each decision permits two command
attempts, then explicitly logs a bounded wait fallback. `--max-decisions` limits
decisions, so command invocations are bounded by twice that number. Model calls
and simulation ticks are reported separately. The JSONL log includes prompts,
responses, validation errors and every executed action result.

## Execution

Candidates include connected housing, a farmland bridge, wheat farming, local
granaries, markets, doctors, Ceres temples, and bounded waiting. The executor
previews construction macros in engine snapshots and restores state afterward.
Only fully successful previews within the macro/tick budgets are offered.
Observed net treasury outlay includes simulation-time income/expenses. A fresh
state fingerprint is checked before actual execution; failure retains partial
progress, which is reported for replanning. The model never receives a direct
Python execution tool. Waiting may terminate or truncate an episode normally.

Limitations: feasible placements do not guarantee useful service coverage;
snapshots and previews add wall-clock overhead; the quake buffer is heuristic;
the vocabulary lacks trade, requests, and many administrative controls. Some
exported monthly production fields remain placeholders and are identified in
the prompt. This runner starts from a clean mission rather than secretly executing
the scripted build order. Candidate previews are not charged to elapsed game
ticks, because their effects are rolled back; actual actions are charged.

## Validation

```shell
python test_planner.py
python test_planner_engine.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

Boundary tests use a synthetic local command, not a real model. Engine checks
cover preview replay preservation, stale-macro rejection, paid construction and
immigration. A live local-model game run must be evaluated separately; no model
strength or autonomous-win claim follows from these tests.

The installed local `qwen3:4b-thinking` model was tried for one live decision.
Both attempts exceeded the default timeout, and the runner logged a wait fallback.
This did not establish successful LLM control. Longer timeout/model tuning remains
necessary for that local setup. Command output is explicitly decoded as UTF-8.

### Token-limited local API adapter

`ollama_planner.py` implements the same command interface using only Ollama's
loopback API and the Python standard library. It requests no thinking output,
sets a 96-token generation budget, trims the prompt to decision-relevant data,
and supplies a JSON schema restricting the current decision and candidate IDs.
It rejects token-budget exhaustion instead of treating partial text as a choice.
The planner still validates the returned object before execution.

```powershell
$modelCommand = '["<ABSOLUTE_PYTHON_INTERPRETER>", "<REPO_ROOT>/python/examples/ollama_planner.py", "--model", "<INSTALLED_MODEL_NAME>"]'
python examples/run_planner.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH> --model-command $modelCommand --model-timeout 120 --max-decisions 3 --max-ticks 1600
```

Ollama must already be serving locally; the adapter never downloads a model.
Adapter `--timeout` defaults to 110 seconds, below the runner's example timeout.
`--max-tokens` accepts 32..1024. Thinking behavior depends on the model; a
thinking-only model may not honor `think=false`. A smaller non-thinking model
may be needed on CPU. Request fields follow the official
[Ollama generate API](https://docs.ollama.com/api/generate).

The runner reports accepted model decisions and fallback decisions separately,
as well as preview, inference and execution wall-clock seconds. Decision logs
retain bounded stdout/stderr excerpts even for rejected replies and timeouts.
Timing data and local API token limits improve diagnostics; they do not establish
successful LLM control by themselves.

### First live control result

The 2026-11-08 exploratory run with local `qwen3:0.6b` accepted three model
decisions and used one fallback, ending with 19 residents at 854 ticks. Its first
two choices were consecutive successful housing macros with no fallback. This
demonstrates live command-to-game control, but not a reliable planner or a win.
The loop remained CPU-latency-limited, and prompt compression was adjusted during
the trial; do not treat it as a fixed-configuration model benchmark.
Use an installed model with `ollama_planner.py --model qwen3:0.6b` to reproduce
the connection with the current adapter. The 4B model remains installed; it was
unloaded from memory after the timeout trial, not deleted.

### Housing observation correction

The initial fixed-configuration follow-up returned two valid waits and attracted
no residents. Reviewing the observation exporter also revealed a separate input
bug: housing capacity was hard-coded to zero. It now sums the physical capacity
of active and newly created house records using the engine's house models.
Housing counts are calculated from the same records rather than a periodically
updated cache. This is physical capacity, not a guarantee of road access or
immediate migration eligibility. Rebuild the library to use the correction.
The local prompt explicitly states that immigration requires housing; factual
game prerequisites are supplied to the model rather than forcing an action ID.

### Observing macro effects

`--decision-interval 400` advances at least 400 simulation ticks per decision
cycle, except on failure, episode end or insufficient remaining budget. The
default remains zero. Construction and automatic observation steps are logged
separately as `macro_ticks` and `observation_ticks`; every step counts toward
the simulation horizon. A selected wait macro already taking 800 ticks receives
no extra observation. The model is told the interval in its context.

This is a different execution cadence, not free time or evidence of a better
model. Compare runs with the same interval and game horizon. In the original
zero-interval eight-decision trial, the model chose housing eight times, consumed
only 164 ticks and ended before immigrants arrived. Increasing only the decision
budget did not ensure observation of meaningful game effects.

Candidates now include housing and safety services near existing wheat farms.
The farmland-connection macro is unavailable when a farm site is already reachable,
so its name does not misleadingly offer redundant bridges as new access. Local
summaries distinguish unemployed workers, employed workers and unfilled jobs,
and include farm recruitment and city health diagnostics.

### Composed Food Supply

`establish_wheat_supply` offers a higher-level alternative to separate farm,
housing, granary and market choices. It generates sites against successive
temporary engine states, connects farmland if needed, places a wheat farm,
worker housing, granary, market and safety services, then restores the original
state. The normal outer preview validates the returned sequence again before
offering it. The same 128-action bound, treasury rules and elapsed-tick budget
apply. Candidate benefit text identifies the combined infrastructure.

This encodes execution knowledge, not a forced strategy: the model may choose
it or another candidate. It is offered when no active wheat farm exists.
Successful construction does not promise adequate labor, food production or
household delivery. The clean-mission integration test executes 50 actions and
verifies all components and subsequent immigration:

```shell
python test_food_macro.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

Feedback retains the last candidate ID even when observation no-ops follow a
macro. Summaries include existing markets, granaries, staffed counts and Ceres
temples, so low current ratings are not the only signal of recent construction.

### Model Compatibility And Sampling

This adapter requests **non-thinking** final JSON. Explicit Qwen3 `-thinking`
tags are now rejected before inference: the publisher's
[4B Thinking model card](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507)
states that it supports only thinking mode. Earlier fixed trials forced
`think=false`; their execution/replay evidence remains useful, but they are not
valid measurements of that model's intended planning capability. The tag guard
is not comprehensive model discovery: custom aliases and other model families
still require checking their documented supported mode.

For a separately installed non-thinking model, the
[4B Instruct model card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
recommends temperature 0.7, top-p 0.8, top-k 20 and min-p 0. The corresponding
[Ollama Q4_K_M tag](https://ollama.com/library/qwen3:4b-instruct-2507-q4_K_M)
is about 2.5 GB. The adapter never downloads it automatically.

```shell
python examples/ollama_planner.py --model qwen3:4b-instruct-2507-q4_K_M --temperature 0.7 --top-p 0.8 --top-k 20 --min-p 0
```

This is a stdin/stdout command adapter: invoke it through `--model-command`,
or supply a captured context on stdin for a protocol probe. Sampling flags are
validated and recorded with inference metadata. Temperature defaults to zero
for backwards compatibility; other sampler fields are left at model defaults
unless explicitly set. A sampling change is a new configuration, not a claim
of better game strategy or repeatable model decisions.

### Food Flow And Observed History

The provider-independent context now separates physical granary, market and
household inventories from the city's cached granary-stock indicator. Farm
progress remains work points, not edible stock. Compact food rows show position,
workers/required workers, the current native local road-access predicate,
inventories, free granary space and farm progress. Samples include at most four
rows per kind, with omitted-row counts; totals include every active row. Cargo
and warehouses remain outside this view, so it is not total city food accounting.

The runner retains the last four actual decision cycles, including failures and
terminal cycles. Each records elapsed paid ticks, status, and net changes in
population, household food coverage, health, culture, separate food containers
and treasury. They appear as `recent_outcomes` in the next decision's context and
as `observed_outcome` alongside the action log. These are observations over time,
not estimates that construction alone caused those changes. No ranking, reward,
forced build order or duplicate-building prohibition is added.

Optional forecasts now include physical granary and market inventory amounts.
The existing legality, construction outlay, observation-interval and tick-budget
rules remain unchanged. Rebuild the library for the separate food query and its
new end artifact; see [RUNS.md](RUNS.md).

```shell
python -m unittest discover -s . -p test_planner_feedback.py
python test_food_supply.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

### Peaceful Culture Actions

Each of the existing well-based district anchors can now offer a school,
library, theater and actor colony, subject to normal availability, footprint,
cost and engine-preview rules. The existing four-district and 128-action caps
remain. An actor colony uses the engine's 3x3 footprint; the other three use
2x2. No campaign data, combat behavior or forced build order changes.

The model receives counts for these buildings and the factual prerequisite
that theaters need performers from actor colonies. Counts do not imply staffing,
coverage or active performances. Placement anchors remain heuristic rather than
guaranteed short-distance coverage. Optional forecasts now include actual culture
alongside population and food outcomes, so the new actions' relevant effects
are not omitted from the lookahead.

```shell
python test_culture_macros.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

The engine regression builds all four kinds through paid actions, observes
positive culture, checks building counts, preview rollback and an independent
simulation suffix. The tested starter reached culture 60 at 4800 ticks. This
validates executor capability, not autonomous mission completion.

### Optional Outcome Forecasts

`--forecast-ticks 1600` adds an optional no-further-construction continuation
to each candidate preview, including waiting. The default is zero (disabled);
the maximum is 8000. This is a minimum total preview duration, including the
macro's construction ticks, clamped to the remaining episode budget. The actual
duration and end status are reported. Longer macros can exceed a shorter
requested duration, so compare the reported tick counts.

Forecasts report population, culture, treasury, food stocks, household food coverage,
health and farm workers from the real simulator. Construction legality and net
construction outlay remain separate. A legal macro whose continuation loses or
truncates is still offered, with that forecast outcome visible. Forecasting
never adds waiting to the selected macro or consumes live simulation ticks;
`--decision-interval` remains the independent charged execution cadence.

The compact local adapter carries forecast columns only when enabled. More
lookahead increases preview cost and prompt size; it is not a long-term food
security guarantee and does not assume any later model construction decisions.
All branches restore their original state, including on exceptions. Test real
engine rollback, outcome equality and budget limits with:

```shell
python test_forecast_engine.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

A fixed three-decision local `qwen3:0.6b` trial with an 8000-tick requested
forecast and 800-tick execution interval selected wait, housing, housing. It
stopped at the decision budget after 2400 ticks with 49 residents, three accepted
choices and no fallback. Independent action-log replay matched. The run folder
ends `planner-local_511a20f1`; previewing took about 24.7 seconds and inference
243.9 seconds. This demonstrates forecast transport and rollback, not improved
strategy, food security or a mission win. Its budgets/token limit differ from
the longer construction-only trial, so it is not a controlled quality benchmark.

### State and terminal-outcome corrections

Rebuild the shared library after the state-token changes. Freshness now includes
an engine-issued identity for every reset and step. Snapshots restore their saved
identity, while a non-restored issuance counter keeps new branches distinct.
The identity is scoped to the Python environment instance. Time-only changes
therefore invalidate old candidates even when the exported city metrics do not
change. The observation/config struct ABI remains unchanged.

Previews accept both completed macros and engine-confirmed wins; defeats,
truncation and failed construction are not offered. Execution reports `won` or
`lost` for authoritative victory outcomes instead of collapsing both into
`terminated`. Other termination reasons remain separate from confirmed victory.
The current runner summary still needs richer outcome and performance accounting
before cross-model benchmarking.

### Experimental two-step native previews

`julius_gym.compound` provides an additive Python interface for one or two
candidate-name steps. `validate_short_plan(proposal, context, candidates)` accepts
exactly `decision_id`, `candidate_ids` (a list of one or two names), and `reason`.
It binds the plan to the initial candidate fingerprint and requires the first
name to be in the current legal menu. The second name is conditional: its
availability and placement are resolved from a newly generated successor menu.
A district index or building ID in a name does not promise stable coordinates
or identity across states. Candidate objects and proposed action arrays are
never accepted as future steps.

`preview_short_plan(env, plan, observation, mission, budget, minimum_ticks=800)`
regenerates and engine-validates each step, uses the existing charged execution
cycle, and restores one outer native snapshot on success, failure or exception.
It rejects stale initial plans and observations using current native scalars
(`env.get_observation()` reads these without advancing time). Budgets are 1..8000
ticks; per-step minimum durations are 0..800. Both construction and observation
ticks consume the budget. A failed, terminal or unfinished step stops the plan;
an unavailable successor returns the valid prefix as `invalid_successor`.

The returned `plan` and `control` branches retain raw actions/messages/rewards,
actual ticks and status, all scalar observations and six final diagnostic
payloads. Executed plan stages also retain before/after state, raw diagnostics,
construction/observation tick counts and net treasury change across the whole
stage (including simulation income/expenses; this is not a quoted build cost).
The control waits from the same base for the plan's actual charged ticks.
Check both `plan.valid` and `equal_time`: an invalid prefix is not an accepted
plan, and an early terminal control can have unequal duration. Neither field
assigns a strategic score. Exceptions propagate after restoration.

The standard `run_planner.py` command does not use this interface. The separate
experimental command is described below. Validate the native foundation with:

```shell
python -m unittest discover -s . -p test_compound.py
python test_compound_engine.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

The native check uses fixed engineering fixtures, explicitly marked as not
model-proposed. It checks all six diagnostics at stage boundaries and after
rollback, then continues directly from the restored base with raw actions.
It retains real saves and traces under the normal Tarraco run convention for
fresh-process verification with `examples/replay_run.py`. Run without `-O`:
disabled assertions are refused before native execution. These controls establish
preview fidelity; they do not establish autonomous improvement or a campaign win.

### Bounded compound model experiment

`examples/run_compound_planner.py` is a separate experimental command. It keeps
the installed instruct model and sampling settings recorded in the planner results.
Each decision makes three audited local API calls: choose a first macro from the
complete current menu, choose a second from its simulated successor menu, then
select among the resulting compound, that same first macro followed by waiting,
and waiting alone. Every final alternative lasts 1600 native ticks. Future names
come from the actual successor menu, without guessed building or district IDs.

The proposal and selection contracts are checked separately. Invalid proposals,
incomplete/token-limited inference, missing context headroom, unequal/partial
previews or audit-write failures stop the experiment; there are no retries or
fallback actions. Final output is ID-only. Native evidence is adapter-owned and
free-text proposal reasons are not verified factual reasoning. The single-macro
control shares the model's root choice; this is a feasibility test, not a controlled
comparison with an independently optimized one-step policy.

```shell
python examples/run_compound_planner.py --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH> --max-decisions 4
```

The command caps execution at four decisions/6400 ticks within an 8000-tick
episode, with at most twelve API attempts at 170 seconds each. Archives retain
full source/library hashes, exact requests/raw responses, native successor
contexts, preview/comparison payloads, selected IDs and execution verification.
Every actual primitive action is logged immediately, including a partial failed
macro. Real saves and six final diagnostics use the normal run directory format.
Use `examples/replay_run.py` for independent replay. The existing live planner
command and its defaults are unchanged.

`successor_context(...)` and `execute_short_plan(...)` are the underlying Python
interfaces. The former always restores its one-cycle simulation and returns a
JSON context without future candidate objects. The latter shares the preview
rollout and regenerates legal candidates at every actual successor; it retains
partial progress on failure. Its optional `on_step` callback receives each
returned primitive result before another action runs. A callback error propagates
and stops execution; native effects already delivered cannot be rolled back.

### Frozen compound presentation diagnostic

`examples/probe_compound_order.py --source-run <ABSOLUTE_SOURCE_RUN_DIRECTORY>`
is an input-only probe on the two designated comparisons from the verified
2026-11-22 run. It checks immutable historical manifest/request/response/audit
hashes before inference. A different native run requires a separately specified
diagnostic; there is no flag to bypass the source anchors.

The probe presents all six row/schema-enum permutations on decisions 2 and 3,
then repeats each original-order request exactly, for fourteen final-selection
calls maximum. All native values, labels and system instructions are retained.
Every call adds seed 20261122 to the previous sampling profile; historical
unseeded choices are not paired controls. Row and schema order change together,
while fixed system-label order remains a limitation. Repeated-control agreement
is checked rather than assuming the seed guarantees determinism.

Archives under `runs/planner-input-probes/` retain original historical records,
source snapshots, complete frozen inputs, every condition/request/raw response,
strict inference telemetry and a final manifest. Missing or contradictory audits
fail acceptance and report unverifiable counts as unknown. No query/proposal API
calls, native environment, game actions, new save or native screenshot are produced.
Refer to the original run's save/replay for native evidence. This helper does not
change any live selector or establish campaign improvement.

### Frozen thinking-profile feasibility check

`examples/probe_compound_capability.py --reference-probe <ABSOLUTE_ORDER_PROBE_DIRECTORY>`
uses the exact pinned prior order archive. It requires the already installed
instruct and thinking model digests; it performs no installation or native action.
Model metadata/templates/defaults are retained before and after inference.

Two instruct original-order controls must reproduce before a thinking canary on
saved decision 3. The candidate enables thinking with a 1536 generated-token cap,
the same 8K context and 170-second hard process/acceptance deadline. The model,
thinking mode and output allowance differ, so this compares profiles rather than
isolating thinking alone. All native facts, prompts, labels, sampling and seed
are preserved. The separate thinking field is retained as unverified output.

An incomplete, length-limited, timed-out or invalid canary stops the check with
no retry or raised budget. If it succeeds, the command completes all six orders
on each saved state and two exact repeats, counting the canary in that sweep:
sixteen inference calls maximum (two instruct and fourteen thinking), zero query
or proposal calls and zero game ticks. Copied reference records and per-call raw
evidence remain local under `runs/planner-input-probes/`. Observations and verified
gates are separate; missing audits or identity evidence withdraw success gates.
Neither feasible reasoning output nor stable selection establishes better native
campaign play. Existing planner commands and previous probe profiles are unchanged.

The first real check stops after two accepted instruct controls and a rejected
thinking canary: 19 generated tokens, complete stop telemetry, empty final
`response`, and answer-shaped JSON only in `thinking`. That output is never
promoted to a final answer. The thinking sweep is unassessed; see
`docs/PLANNER_RESULTS.md`. The failed archive and original gates remain unchanged.

For future checks, metadata identity ignores parameter-group display order and
the redundant generated Modelfile text. It still compares effective values,
ordered repeated values, exact templates, digests and other model metadata;
raw before/after responses remain archived. This fixes a presentation-only
identity alarm in that first run without accepting its failed canary.

`examples/probe_compound_channel.py --reference-probe <ABSOLUTE_ORDER_PROBE_DIRECTORY>`
is a separate four-call transport diagnostic on frozen decision 3. It varies only
provider `format` presence in schema/omitted/omitted/schema order. The thinking
model, native facts, prompts, seed, sampling, 1536-token cap and 170-second
deadline are fixed. Exact client-side final JSON validation is always required.
Complete rejected outputs are recorded; transport/deadline failure stops the
remaining conditions. Metadata/reference/audit failures withdraw verified results.
This does not change the live planner or reopen the failed capability gate.
