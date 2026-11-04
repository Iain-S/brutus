# Local model planner

`run_planner.py` runs a decision loop over a small macro vocabulary. It does not
require the scripted controller to win first. This is an initial planner interface,
not a demonstrated LLM solution to Tarraco.

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
