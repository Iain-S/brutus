# Peaceful campaign planner: Tarraco

## Imperial Capability And Water Audit: 2026-11-11

Three appended gift actions now use the normal emperor path, paid from personal
savings with unchanged costs and diminishing returns. A separate read-only
imperial query exposes salary, savings, favor, timing/penalty and fresh gift
quotes without modifying GUI caches. The planner receives this factual state,
legal gift choices and favor/personal-savings forecasts. No gift schedule or
winning build order is forced. Request dispatch and salary controls remain
unimplemented. Action IDs 0-55 are unchanged, but the space is now 59 actions;
old fixed-action-space RL checkpoints require their old build or migration.

Native tests cover quote immutability/buffer guards, personal rather than city
payments, all sizes, affordability boundaries and diminishing returns. The
asset-backed test funds gifts through ordinary salary, checks candidate preview
rollback and waits for the native 12-month recovery. Future run bundles include
`final.imperial.json`; replay compares the entire diagnostic payload when present
and remains compatible with older bundles lacking it. These are capability
checks, not autonomous wins or full-state GUI-cache coverage.

The independent housing audit identified a stronger remaining barrier. Read-only
inspection of the currently loaded original house models confirms that the
maximum prosperity contribution without fountain water is 20. Small hovel
(level 4) contributes 25 and requires fountain water, one food type, religion
and suitable desirability. Pottery is not required at that tier. Native city
prosperity is capped by the unweighted house-model average, so the current
well-only vocabulary cannot reach the active target 25 from this initial city.
Loaded-model observations are retained in ignored `runs/housing-model-audit.json`;
model data was not modified or copied into tracked source.

Working fountains require workers and a supplied reservoir's range. Gym exposes
fountain construction, but no reservoir/aqueduct actions, and the planner offers
no fountain candidates. Next add and test the complete normal water-supply
capability, not a decorative unsupplied fountain or altered house requirements.
Then verify prosperity growth, scalable district coverage and economic controls
before another long model trial. The first four well anchors still limit the
current district-service search; population 2500 has not been demonstrated.

## Intact-Input Trial And Mission Reachability: 2026-11-10

Source `894e216f`, run `planner-local_2c28aa7a`, repeated the objects-mode
configuration with only the requested context budget raised to 8192. All 16
decisions were accepted without fallback. At 12800 paid ticks the city had 140
residents, culture 40, 70 residents holding food, 259 household food units,
404 market units and empty granaries. There was no win. The model chose eight
schools, a theater, the wheat-supply macro, another farmland connection, two
farms, two farm-worker housing macros and a market; no general housing expansion.

Peak prompt length was 5098 tokens, leaving 2838 after reserving the 256-token
response budget. Runtime capacity was verified as 8192 with GPU offload and no
server prompt-truncation entries. Previewing took 129.6 seconds, inference
383.2, total wall 515.8. Independent replay `replay_01b87cea` matched per-step
results, final buildings, population, victory and complete food diagnostics.
Standard final saves and runtime sidecars are retained; PNG capture is manual.

This resolves the observed input-capacity failure for this bounded trajectory,
not the planning problem. Repeated schools still yielded no additional culture
in several recorded cycles, and housing growth remained limited. One stochastic
trajectory does not isolate context size as the cause of the population change.
The default remains 4096/rows; use the explicit settings to reproduce this trial.

Before spending more calls on longer runs, account for two source-level limits:

- `src/city/ratings.c` updates peace annually: the first two clean years add two
  points each, then clean years add five. Starting at zero, the best sequence is
  2, 4, 9, 14, 19, 24, 29, 34. Thus peace 30 requires at least eight annual
  updates, even without crime or destruction. A roughly 16-month trial cannot
  demonstrate a complete win; these trials measure partial development only.
- `src/gymnasium/action.h` exposes construction, tax and wage controls, not
  imperial gifts, request dispatch or governor salary. In ordinary peaceful
  play these omissions block the normal favor-management routes. The observed
  starting favor is 50 and the target is 70; the three milestone bonuses in
  `src/city/ratings.c` add at most 15 even before annual losses. Gifts and
  fulfilled requests use the normal engine in `src/city/emperor.c` and
  `src/scenario/request.c`, but are not reachable through the current adapter.

A read-only native reset inspection confirmed that all five targets are active:
population 2500, culture 45, prosperity 25, peace 30 and favor 70, with initial
peace zero and favor 50. This is an action-capability/horizon issue, not something
a better model alone can solve. The inspection executed no game actions.

Next checkpoint: audit coverage of every active win criterion, then expose and
test missing lawful imperial observations/actions, including personal savings,
actual gift costs and diminishing returns, without granting money/favor or
forcing a gift schedule. Also verify housing evolution/prosperity capabilities
and choose a horizon consistent with normal peace progression. Do not weaken
the mission goals or accelerate the engine's annual ratings.

## Explicit Context Budget: 2026-11-10

The local adapter now accepts `--context-tokens 8192` (allowed range
2048-16384, unchanged default 4096). This changes only Ollama's requested
`num_ctx`; the chosen value is already included in stderr `options` metadata
and the run's model-command configuration. Prompts, candidate availability,
sampling, response budgets and game behavior are unchanged. Larger contexts
may increase GPU/CPU memory use and inference time.

For named forecasts, verify representative large inputs, actual loaded context
capacity and server truncation logs before interpreting decisions. Reserving
space for the output and some growth is necessary; simply accepting JSON is
not a context-integrity check. A verified fixed trial does not guarantee that
arbitrarily larger future states will fit.

Preflight of the three largest saved objects-mode prompts reported 4204, 4188
and 4158 input tokens at an actual loaded capacity of 8192. Each completed with
valid current-decision JSON, verified GPU offload and no server truncation.
After reserving 256 output tokens, the smallest remaining margin was 3732.
This verifies those saved inputs only; another live trajectory still needs its
own prompt-count and server-log checks.

## Optional Named Forecasts

The local adapter accepts `--forecast-format objects` to send candidate
forecasts as dictionaries instead of positional rows. The default remains
`rows`; no facts, action availability, ordering or sampling settings change.
The chosen format is recorded in adapter stderr metadata. With forecasts
disabled the flag does not invent them. Objects consume more context: three
captured probes grew from 2506-2673 to 3447-3614 tokens of the current 4096.
Check prompt counts and Ollama truncation logs before interpreting live results.

The first live objects-mode trial (`planner-local_b502c162`, source `51aa6abd`)
confirmed this headroom risk: six prompts of 4114-4204 tokens were truncated to
4096 by Ollama. It ended at 12800 ticks with 90 residents, culture 40, 30
food-holding residents, 97 household food units, 488 market units and no win.
All 16 choices were accepted without fallback, but accepted JSON does not mean
the model received the complete state. Ten choices were schools; no general
housing expansion was chosen. Previewing took 131.2 seconds, inference 292.5,
total wall 426.5. Strict independent action replay, including detailed food
state, passed. The usual final save and runtime diagnostics are retained.

Do not interpret this trajectory as a clean demonstration of improved strategy:
later decisions used truncated inputs, and the run was stochastic. The adapter
default remains rows. Next add an explicit audited context-budget setting,
preflight the largest captured contexts, and verify no truncation before another
comparison. Do not silently discard candidates or introduce a forced build order
to make the prompt fit.

In one paired sample at each of three saved decisions, named forecasts selected
actions with higher forecast culture than the row form. This is input-format
sensitivity and a reason for a bounded live test, not evidence of a faster win.
No human-directed build order or duplicate-construction filter is introduced.

## Compatible instruction-model result: 2026-11-09

The first full trial with `qwen3:4b-instruct-2507-q4_K_M` used source
`061400a9`, the corrected housing-access generator, temperature 0.7, top-p 0.8,
top-k 20 and min-p 0. The installed manifest digest is
`0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`.
The adapter/executor remained unchanged throughout all 16 decisions, with
12800 paid ticks, 800-tick decision intervals and 1600-tick forecasts.

Run `planner-local_d4aa46fd` ended with 83 residents, culture 15, seven residents
holding food, 28 household food units, 172 market food units, empty granaries
and no win. Choices were one housing expansion, four markets, a farmland
connection, a wheat farm, farm-worker housing, five granaries and three schools.
All 16 responses were accepted without fallback. Prompts peaked at 2673 of
4096 tokens, with no server prompt-truncation entries. GPU offload was verified;
previewing took 125.8 seconds and inference 166.6 seconds (295.2 seconds total).

Independent action replay `replay_3e8dcb85` matched per-step messages/rewards,
final buildings, population, victory and the complete food-supply payload.
The source bundle retains `model.runtime.json` with the installed digest,
native-library hash and GPU metadata, as well as the normal `final.sav` for
Julius review. Rendering remains manual; no end PNG has been generated.

This establishes a working supported-mode baseline, not competent play. The
model repeatedly chose storage despite empty granaries, labor shortages and
available housing forecasts with greater population. Some duplicate schools
also produced no additional culture during their recorded cycles. These are
observations from one stochastic trajectory, not proof that duplicates are
universally bad or that the model family cannot plan. Mode, sampling and the
housing fix all differ from earlier trials; no model-only causal comparison
is justified. Do not extend the horizon blindly or add a prescribed build
order. Next isolate whether the compact positional forecast representation
is impairing decision quality, using captured contexts before another live run.

## Housing proposal legality: 2026-11-09

The housing outage after about eight blocks was not a game population cap.
Audit of run `planner-local_98c9fe3d` found that the ninth proposed block first
placed an access road at `(35,52)`, then tried to put a house on that road. The
strip was checked against the original map, but not against its own newly
planned access path. Preview correctly rejected construction; the generator
had failed to continue searching despite other viable sites.

The starter generator now rejects access paths intersecting the entire future
strip and continues its existing search. This also avoids duplicate planned
road actions. Two synthetic regressions and a native nine-block test reproduced
the failure before the fix and pass afterward. No population, migration,
construction cost, campaign event or strategy rule changes. Remaining siting
heuristics, forest exclusion and strip shape are unchanged.

The compatible instruction-model download and three captured-context preflight
checks succeeded, with GPU offload and the existing models retained. The first
full instruction trial uses this legality correction, so it must not be treated
as a controlled model-only comparison against earlier broken-mode trials.

## Food observations and model-mode correction: 2026-11-09

The separate native food-supply query now reports edible farm work progress,
physical granary/market inventories and relevant staffing/road context. It does
not reinterpret partial production as food, count free space as inventory, or
claim cargo/warehouse visibility. New runs retain `final.food_supply.json` and
replay compares it strictly when present; older building diagnostics are intact.

The planner now receives bounded food samples and four recent actual cycles,
including stock, household-food, population, culture, health and treasury
changes. These are elapsed-cycle observations, not causal estimates. There is
no forced strategy, ranking or duplicate-construction prohibition.

A fixed 16-decision trial (suffix `planner-local_98c9fe3d`) ended at 12800 ticks
with 310 residents, eight empty granaries, no farms/markets, no food and no win.
All 16 responses were accepted without fallback; independent replay, including
detailed food state, matched exactly. Prompts peaked at 3297 of 4096 tokens,
and the server logged no prompt truncation. Previewing took about 210.9 seconds,
inference 219.7 seconds. Richer input did not establish improved strategy.

Investigation found a major configuration confound: the installed
[Qwen3-4B-Thinking-2507](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507)
supports only thinking mode, but these trials requested non-thinking JSON.
Do not use the preceding trials to judge its intended reasoning capability.
The adapter now rejects explicit Qwen3 thinking-only tags and exposes validated
sampling controls. A separate
[non-thinking instruction variant](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
is the next comparison target; its download has now completed. Existing weights
are retained. A captured-context probe with the installed hybrid 0.6B model
verified the new sampling flags and valid final JSON only; no game actions were
executed and no strategic-quality claim follows from that probe.

The scripted food-preview regression also compares detailed inventories,
production work and raw figure references against clean-reset action replay
without previews at eight cycle boundaries. It passes with the new query.

## Peaceful culture capability: 2026-11-09

School, library, theater and actor-colony candidates now use existing engine
construction actions at the current well-district anchors. The model receives
their building counts, the theater/actor prerequisite, and actual culture in
optional forecasts. No build order is forced; campaign and combat rules are
unchanged. The native integration test constructs all four, observes culture 60
at 4800 ticks, and checks preview rollback and an independent simulation suffix.
The three-way inhabited preview/no-preview comparison also passes.

A fixed 16-decision follow-up with the same model, execution interval and tick
horizon ended at 12800 ticks with 340 residents, 60 residents holding food,
16 accepted choices, zero fallback and no win. Its run suffix is
`planner-local_203e3d06`, with the usual end save for Julius review. Independent
action-log replay matched exactly. Prompts peaked at 2743 tokens with the
4096-token context setting; this bounded run showed no context-limit hit, not
a guarantee for arbitrary future candidate sets. Previewing took about 220.7
seconds and inference 189.0 seconds.

The agent chose seven housing expansions, the wheat-supply macro while housing
was still available, seven extra markets and one extra granary. The endpoint
had one farm, eight markets, two granaries and no culture buildings. Delivery
improved relative to the prior trial's 19 food-holding residents, but most
residents still lacked food inventory and culture remained unaddressed.
New choices being executable does not establish that the model uses them well.
The runs differ in objective transmission, observations, choices and forecasts,
so this does not isolate the cause of any change in model behavior.

Next prioritize diagnostic food-flow visibility and evidence-based planner
feedback rather than adding a hand-coded market/food/culture build order.
Placement locality, housing expansion, health and full rating management remain
limitations before a credible full-mission optimization experiment.

## GPU-backed 4B trial: 2026-11-09

After repairing local GPU inference, an unchanged adapter trial used installed
`qwen3:4b-thinking`, explicitly with `think=false`, a 256-token response cap,
16 decisions, 800 charged ticks per decision, and 1600-tick forecasts. It ended
at 12800 ticks with 355 residents, 16 accepted choices, zero fallback and no win.
Inference took about 132.6 seconds, previewing 128.3 seconds. The run suffix is
`planner-local_dd6a7645`; final saves and building diagnostics follow RUNS.md.
Its recorded actions independently replayed exactly, including across New Year.

Choices were eight housing expansions, a composed wheat supply, an additional
farmland connection, then six extra granaries. The food choice occurred when
housing expansion was unavailable, so it does not prove strategic foresight.
The farm reached ten workers, 100 stored food was observed, and 19 residents
held food at the endpoint. Seven granaries, one market and no doctors remained.
This is initial production/delivery evidence, not a sustainable economy.

At the same 12800-tick horizon, the five-block deterministic baseline with food,
health, religion and quake buffer 14 had 318 residents, 100 stored food, health
66 and 236 residents with food. Its independent replay also passed (run suffix
`baseline_c86b33b2`). These controllers use different construction schedules;
this comparison does not establish the model as faster or better.

Audit found that compacting the model request dropped the fast-win objective;
the adapter now preserves it. Separate C observation errors reported farms,
workshops and total buildings through incorrect count buckets. Aggregates now
use actual active/created records; tests cover positive construction categories,
reset isolation and linked hippodrome venue semantics. These counters were not
in the compact state aliases, so their correction alone does not explain or
fix the model's repeated granary choices.

Executor limitations in that recorded trial matter independently of model size: placement
anchors do not guarantee nearby service coverage, detailed food inventories
are not exposed, and that vocabulary had no education or entertainment actions.
Religion alone cannot reach the culture goal of 45. Expand and validate those
capabilities before presenting any full-mission run as a fair planning test.

Two captured-context `think=true` probes produced no usable final JSON (one
stopped with only a thinking field under structured output; another exhausted
2048 tokens without grammar). Neither response was executed. Reasoning-mode
support needs a separate bounded protocol test, not parsing thoughts as actions.

## Snapshot fidelity checkpoint: 2026-11-09

The fixed-snapshot follow-up reached 245 residents at 6400 ticks, with eight
accepted model decisions and no fallback (run suffix `planner-local_97a7f463`).
Independent replay matched all action messages/rewards and final building,
population and victory diagnostics. Choices were a farmland bridge and seven
housing expansions; no food economy or win was demonstrated.

Review of longer-lookahead boundaries also found transient annual fire-spread
direction and victory/force-win flags outside the save format. Regressions
reproduced a wind change surviving rollback and a speculative victory remaining
visible after restore. Gym snapshots now preserve both without changing normal
game saves. `python/test_snapshot_boundaries.py` exercises annual wind, actual
force-win termination and injected transient defeat rollback; it does not alter
campaign rules in production.

Independent replay of a 3,200-tick local-model run exposed differing service
coverage and fire-risk diagnostics despite matching action messages/rewards.
A regression reproduced the difference using the same bridge/housing sequence
with and without candidate previews. The normal save format stores random
generator seeds but omits cached outputs, pool contents and pool position;
loading a snapshot therefore allowed speculative branches to affect later
population-age sampling and service behavior.

Gym snapshots now separately capture and restore the complete transient random
state after loading their standard save. The save format and normal graphical
loading behavior are unchanged. Both inhabited replay and eight-decision
preview-versus-no-preview checks pass with this fix. Historical runs produced
with the incomplete snapshot implementation should not be treated as verified
comparisons; their logs/saves remain available for investigation.

The small CPU-only local model has produced fallback-free runs, but still
repeatedly chooses housing and has not demonstrated a sustainable food economy
or mission win. Construction previews establish legality, not long-term
usefulness. The next strategy checkpoint remains a food-producing settlement
under local-model control, followed by independent action-log replay.

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

### Fixed-configuration checkpoint: 2026-11-09

Planner corrections, durable artifacts, and the local adapter were committed as
`5b9bd048`. The first unchanged-adapter trial completed two accepted waits with
zero fallback, but no construction or residents. Transport success alone was
therefore insufficient. Source review also found `housing_capacity` was still
a zero placeholder in the C observation exporter.

The exporter now computes physical housing counts/capacity from active and newly
created house records, using the same house-model capacity and merged-house
multiplier as the engine. This is not a guarantee of road access or immediate
migration eligibility. A regression first failed against the zero placeholder
and then passed; construction/reset replay and planner engine tests also pass.

After that correction and an explicit housing prerequisite in the local prompt,
a separate fixed-configuration trial made three model calls and accepted all
three decisions without retries or fallback: housing, housing, farmland bridge.
Capacity observations at those decisions were 0, 40 and 80. The run stopped at
the three-decision budget after 51 game ticks, with zero residents and no win.
Inference took about 93 seconds, previewing about 5 seconds. City growth cannot
be judged from this short construction phase. The final save/log are in the
2026-11-09 run folder ending `planner-local_ed114240`.

The basic fallback-free local-control checkpoint is demonstrated, not mission
competence. Next use a larger decision budget with an explicit simulation
horizon to observe immigration and evaluate food/staffing decisions. Do not
silently add uncharged waiting or equate valid construction with useful strategy.

### Decision cadence and replay: 2026-11-09

The committed zero-interval eight-decision run selected housing eight times,
with no retries or fallback, but advanced only 164 ticks and attracted no
residents before reaching its decision budget. This is not enough time to judge
immigration or service effects.

Commit `1bf08aa9` adds an optional charged observation interval, farm-local worker
housing and safety actions, redundant-bridge suppression, and clearer labor
summaries. A fixed four-decision trial with `--decision-interval 400` reached
1600 ticks and 66 residents, with four accepted decisions and no fallback.
Choices were housing twice and two Ceres temples. This proves population growth
under the loop, not a balanced economy or strong strategy.

`python/examples/replay_run.py` independently reproduced both the 164-tick and
1600-tick runs from reset without model calls or snapshot previews. It checks
per-action messages/rewards and final building diagnostics, population and
victory state. Each replay retains its own manifest and final save.

The eight-decision, 400-tick-cadence follow-up reached 3200 ticks and 201 residents
with eight accepted decisions and no fallback, but selected one farmland bridge
and seven housing expansions, leaving the offered farm unused. Further work now
adds recent-action/service feedback and an optional composed wheat-supply macro.
Its engine test builds the complete district in 50 paid actions with preview
rollback and subsequent immigration. A live choice remains a separate test;
the compound macro does not guarantee a staffed or productive food chain.
