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
- Reset currently calls the scenario loader only when a filename is supplied.
  An omitted filename does not explicitly start a fresh campaign mission.

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
unimplemented. No autonomous win or LLM-controlled episode has been demonstrated.
