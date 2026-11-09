# Local model planner

`run_planner.py` runs a decision loop over a small macro vocabulary. It does not
require the scripted controller to win first. This is an initial planner interface,
not a demonstrated LLM solution to Tarraco.

The compact local request preserves the explicit objective: win in minimum
simulation ticks. Treasury is relevant to feasibility, not a replacement
optimization target. The current candidate vocabulary is still incomplete:
it has no education or entertainment macros, so it cannot yet meet Tarraco's
culture goal. Successful food construction or a higher population is not a win.

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

### Optional Outcome Forecasts

`--forecast-ticks 1600` adds an optional no-further-construction continuation
to each candidate preview, including waiting. The default is zero (disabled);
the maximum is 8000. This is a minimum total preview duration, including the
macro's construction ticks, clamped to the remaining episode budget. The actual
duration and end status are reported. Longer macros can exceed a shorter
requested duration, so compare the reported tick counts.

Forecasts report population, treasury, food stocks, household food coverage,
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
