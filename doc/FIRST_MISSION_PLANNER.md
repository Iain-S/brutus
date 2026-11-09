# Peaceful campaign planner: Tarraco

## Objective

Win Tarraco autonomously and minimize elapsed simulation
ticks to the engine's victory signal. Report wall-clock runtime and model calls
separately. Read the actual victory thresholds from the loaded mission rather
than assuming values from a walkthrough. Target only peaceful campaign choices
and exclude combat from the controller for now. This document supersedes the
original first-tutorial-mission proposal; its filename is retained for continuity.

## Existing integration

- `JuliusEnv.step_at(type, x, y)` already supports coordinate actions.
- `JuliusEnv.snapshot()` supports speculative execution and restoration.
- Observations expose economy, population, ratings, time, and victory goals.
- `get_map_data()` supplies terrain flags and building IDs, but building IDs
  alone do not describe building types, service coverage, or road connectivity.
- Explicit `campaign_rank=3` selects Tarraco's peaceful branch and reloads it
  on reset. The legacy no-scenario default is not used by these runners.

Campaign missions come from the original `mission1.pak`, through
`load_campaign_mission()` in `src/game/file.c`. Tarraco uses campaign
mission index 4 and rank 3 (both zero-based), the peaceful entry in
`src/game/mission.c`. A dedicated campaign reset should select those
properties, mark the scenario as non-custom, and use the normal scenario-start
initialization path. Do not treat the pack as a custom `.map` file.

## Mission-specific constraints

The first two ranks have tutorial population gates. Capua, the first peaceful
choice at rank 2, has no such population cap but is still classified as tutorial
three, with special disease/message handling. Tarraco at rank 3 is the earliest
peaceful choice outside all three tutorial classifications in
`src/scenario/property.c`.

Use normal population, migration, disaster, and mission-event rules. Do not
disable disasters or edit mission data to make a run easier. Before accepting
the mission for a combat-free experiment, inspect its invasion and military
request schedules; the peaceful branch label alone is not a no-combat guarantee.
If combat is scheduled, select the next eligible peaceful mission and record why.

Check construction availability against the same menu rules as
the graphical game. Audit the Gym action path before benchmarking: a successful
construction call is not sufficient proof that a building was unlocked.

## Proposed controller

Use a Python executor with a provider-independent JSON planner interface. Start
with a deterministic baseline through the same interface; this makes it
possible to test the game adapter and quantify what the LLM contributes.

Alternatives are direct LLM tile selection (more placement errors and larger
prompts) and training a policy (requires an environment and training budget).
Validated macro choices provide a small, inspectable starting point for this
mission and leave room for later optimization.

Each decision follows this sequence:

1. Read engine observations, mission events, and map state.
2. Generate a small list of executable candidates, with exact placements,
   estimated costs, preconditions, and stable candidate IDs.
3. Send a compact JSON snapshot and candidate list to the planner.
4. Validate its response and revalidate the chosen candidate against current
   state before execution.
5. Execute a bounded macro, stopping on failure, termination, or truncation.
6. Record the result and obtain a fresh observation before the next decision.

Example planner input (illustrative values, not a captured game state):

```json
{
  "decision_id": 12,
  "elapsed_ticks": 240,
  "population": 800,
  "bottlenecks": ["housing_capacity"],
  "candidates": [
    {"id": "wait_32", "action": "wait", "ticks": 32},
    {"id": "housing_a", "action": "build_housing_block", "lots": 8}
  ],
  "last_result": {"candidate_id": "wait_32", "status": "completed"}
}
```

Example response:

```json
{
  "decision_id": 12,
  "candidate_id": "housing_a",
  "reason": "Add capacity to support further immigration."
}
```

The response chooses an existing candidate. It cannot supply executable Python,
invent coordinates, or mutate game state. Reject malformed, stale, or unknown
choices with bounded retries and an explicit fallback or stop result. Log the
reason for diagnosis; execution depends only on validated fields.

## Executor details

Initial macros: connect a road, place housing beside a connected road, place
a well, place an available prefecture or engineer's post, place a senate when
available, clear a selected ruin, and wait for a bounded number of ticks.
Candidate generation must account for map origin, footprints, terrain, entry
road connectivity, occupancy, funds, and mission construction availability.
Service coverage must come from engine data or a verified model, not proximity
alone.

Waiting executes no-op actions and stops on episode end. Each construction
currently advances simulation time through `step_at`; count every such tick.
A macro is not atomic: failures can leave a partly completed block. Record
completed placements and regenerate candidates from the resulting state.

Snapshots can evaluate alternative candidates without retaining their effects.
First verify replay determinism, including tutorial flags and random events.
Use sequential branches in one environment or separate worker processes:
the underlying game uses global state. Require replay from a clean reset before
accepting any optimized build order as a result.

## Implementation sequence and acceptance

1. Add explicit campaign reset without changing the existing configuration
   struct ABI. Verify mission identity, nonempty map, goals, and repeat resets.
2. Verify the loaded target has no tutorial classification, audit combat-related
   events, and expose construction availability and relevant mission events.
3. Build candidate generation, bounded macros, JSON validation, and action logs.
   Exercise them with a deterministic policy before adding a model provider.
4. Connect an LLM provider configured outside tracked files. Invoke it on macro
   completion or meaningful state changes, with limits on calls and retries.
5. Obtain an engine-confirmed win, replay it from reset, then optimize placement
   and timing. Compare the baseline and LLM using the same mission and settings.

A successful run logs mission identity, difficulty, engine/library version,
model configuration when applicable, action results, elapsed ticks, victory
state, and termination reason. A timeout, bankruptcy, population increase, or
high shaped reward does not count as a win. No optimality claim is justified
merely by finding a winning sequence.

## Current validation status

Tarraco was loaded through explicit peaceful campaign selection using the local
original `mission1.pak`. The engine reports rank 3, mission 4, no tutorial
classification, no scheduled combat events, and no gladiator revolt. Victory
goals are population 2500, culture 45, prosperity 25, peace 30, and favor 70.
The original 128-step replay check was insufficient: Gym used the GUI loop,
which could leave the simulation frozen. Gym now calls one simulation tick per
step, and a 1600-tick reset replay and snapshot replay pass with real game-time
progression. Map export pads outside the active map instead of reading beyond it.
Construction now uses the normal cost, resource, placement and routing pipeline.

`python/examples/run_baseline.py` builds an entry-connected starter settlement
and writes a per-tick JSONL log. A 3000-tick run reached 49 residents with no failed
placements. Food production, further expansion, and rating management remain
unimplemented in the starter mode. The optional `--food --blocks 3` mode now
builds a low bridge to farmland, farm worker housing, a granary and market.
A 12000-tick run reached 182 residents and 1300 stored food without failed
construction; complete logs matched across two fresh runs. Food stocks establish
harvesting and storage, not sufficient delivery to every house. Food produced
and consumed-last-month observation fields are placeholders in the C exporter.
No autonomous win or LLM-controlled episode has been demonstrated.

The subsequent delivery baseline fixes granary center-edge access, keeps bridge
landings open, and places local markets and farm safety services. Read-only
building diagnostics distinguish stored food from food actually delivered to
houses. A 24000-tick, five-block run peaked at 262 residents and ended at 181,
with 2200 stored food, 51 residents holding food, and one surviving farm.
Those results are historical. Health coverage, quake-aware placement, and Ceres
temples subsequently reached 318 residents over 24000 ticks, with health 94,
236 residents holding food, and no recorded occupied-house losses. Food reserves
and service coverage still need work; this is not a mission win.

## Plan Review: 2026-11-04

The separation of planner strategy from engine-validated placement remains
appropriate. A deterministic win is not a prerequisite for LLM integration.
Campaign loading, deterministic execution, local-command JSON selection,
snapshot previews, bounded retries, and explicit fallback are implemented.
The boundary and engine smoke tests pass. The local Qwen attempt timed out
twice; fallback waiting does not count as a successful model decision.

Review identified prerequisites for the next checkpoint:

1. Replace observation/map-only freshness checks with a reliable execution
   revision or exact tick token that also tracks resets and snapshot restores.
   A one-tick wait currently leaves the fingerprint unchanged and permits reuse
   of an old candidate. Add a regression for time-only state changes, not just
   a construction macro that visibly changes the map.
2. Preserve engine-confirmed winning preview outcomes. Current filtering only
   accepts `completed`, discarding all terminal macros. Distinguish victory,
   defeat and truncation in previews, execution logs and final reports. Add a
   focused terminal-outcome regression; a real mission win is not needed to
   exercise this control-flow case.
3. Improve run accounting before performance comparisons: include explicit win
   status, fallback count, wall-clock inference/preview/execution time, and model
   configuration. Current logs contain chosen responses, but rejected raw model
   responses are lost, and the final summary does not distinguish defeat from
   victory. Snapshot search overhead must remain visible alongside game ticks.

Next checkpoint acceptance is two consecutive valid local-model choices from
fresh candidate sets, with at least one useful construction macro followed by
observed game progress. Require no fallback for those choices and retain the
full execution record. Use a short game horizon while tuning local inference;
do not spend full mission-length runs debugging model transport.

After that checkpoint, compare against the scripted baseline using equal
mission settings and simulation horizons. Expand the action vocabulary where
observed failures justify it: farm-worker housing and local safety services,
additional production sites, requests/trade, and rating-related construction.
The current four-district candidate cap and missing controls are prototype
limits, not evidence that the LLM can solve the full mission. Reliable wins,
clean-reset replay, and then completion-time optimization remain later gates.

### Correctness follow-up: 2026-11-07

Items 1 and 2 above are implemented. Engine-issued state tokens track every
step/reset and restore snapshot identity without reusing new-branch identities.
Tests cover time-only advancement, reset invalidation, branch uniqueness and
preview replay. Terminal execution distinguishes won/lost, and winning previews
are retained. Seven boundary tests and the engine integration test pass after
rebuilding the library. Run accounting and the live-model checkpoint remain open.

### Manual review proposal

Capture one persistent `final.sav` at the end of a run, including timeout/defeat,
before closing the environment. Current speculative snapshots delete their
temporary files and are not a durable review artifact. Add an explicit save
export rather than relying on those private filenames.

For an authentic image, load the save in graphical Julius and use its existing
full-city screenshot renderer (`graphics_save_screenshot(1)`, Ctrl+F12). This
uses the original loaded game assets and produces a whole-city PNG without the
normal HUD. Preserve the save alongside the image for interactive inspection.
For Tarraco's 80x80 map, the current renderer computes 4800x2430 pixels.

The first implementation is save export plus manual GUI loading and
screenshot capture. Baseline/planner runners now export `final.sav`, diagnostics,
and a manifest in unique UTC-stamped folders under `runs/tarraco/YYYY-MM-DD/`.
This includes ordinary exits and errors after a successful reset. See
`python/examples/RUNS.md` for the naming convention and limitations.
Automatic `final.png` export would be a separate graphical
render step: load paused, initialize the real canvas/assets, render without
advancing simulation, and write a deterministic output filename. Calling the
screenshot routine from the training DLL alone is insufficient because it
requires a city window and graphics canvas. Persistent save export is implemented;
automated GUI rendering remains unimplemented. Tests cover unique naming,
error manifests, and persistence after truncation and environment cleanup.

### Local control trial: 2026-11-08

The installed 4B thinking model still timed out when run with non-thinking
requested. Server logs showed CPU-only inference with three threads. A smaller
local `qwen3:0.6b` model was downloaded, and a token-limited loopback API adapter
was added behind the existing command protocol. Its schema restricts the current
decision and candidate IDs; the model still chooses the action and reason.

The small-model trial produced two consecutive valid, successfully executed
housing macros without retries or fallback. Across all four decisions it made
six inference calls: three decisions were accepted and one used fallback wait.
The game reached 854 ticks and 19 residents, with no victory. Inference consumed
about 516 seconds, versus 9.6 seconds previewing and 0.2 seconds executing macros.
This demonstrates the initial control interface, not strategic competence or a
reliable fallback-free loop. The small model repeatedly chose housing expansion.

Prompt compression was tuned during this exploratory run, so its results are
not a fixed-configuration performance benchmark. The final adapter now includes
housing capacity, elapsed ticks and short candidate rows. Full engine context,
bounded raw model output/error excerpts, retry counts and timing are retained.
The run is under `runs/tarraco/2026-11-08/` with suffix
`planner-local_bf8bb37d`, including a persistent final save for manual review.

Next, verify a fixed adapter configuration over a fully fallback-free short run
before extending game horizons. Then evaluate whether decisions address food,
staffing and services instead of repeatedly expanding vacant housing. Eleven
boundary/adapter tests and the engine replay test pass; model quality still
requires live evaluation rather than synthetic command fixtures.
