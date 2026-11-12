# Water Labor Snapshot Repair Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans, systematic debugging, TDD and independent source review. Preserve staged models and historical run artifacts.

**Goal:** Prevent speculative forecasts from changing the native round-robin water-worker allocation cursor in the live simulation.

**Evidence:** Fixed local trial `planner-local_e2122189` accepted 16 decisions
with zero fallbacks, 12,800 ticks, population 76 and prompt peak 7,167/8,192.
However, strict independent `replay_5a59fe42` failed final buildings: two workers
were assigned to a different fountain and two houses differed in fountain
coverage. Water/housing diagnostics confirm the differences; food, imperial and
finance match. Every step message/reward matched. This is NOT a validated
strategy result. The representation experiment was not started.

**Root-Cause Candidate:** `allocate_workers_to_water()` in `src/city/labor.c`
retains function-static `start_building_id`, rotating distribution when water
labor is scarce. Native saves and Gym snapshot extras omit it; preview restores
can therefore alter future live staffing despite an unchanged immediate map.

**Architecture:** Keep the native allocation algorithm and GUI semantics intact.
Move only the cursor storage to module scope and add minimal capture/restore
helpers. Initialize Gym episodes to the original cursor value 1; capture it in
opaque Gym snapshots and restore it after native save loading. No public Gym
observation/config/action ABI or native save format changes. Do not relax replay
comparisons, rewrite old artifacts, remove rotation or guarantee staffing.

**Tech Stack:** Existing C shared library/native tests, Python ctypes and paid recorded-action controls.

## Tasks

- [x] Independently verify the cursor lifetime and mutable allocation state.
- [x] Add failing isolated scarcity/rotation/cursor tests and snapshot/reset hook tests, then implement the minimal capture/restore/reset integration.
- [x] On a freshly reset fixed library, execute the old recorded action sequence twice: baseline without previews and the same steps with interleaved normal full candidate forecasts. Compare every step and all six final raw diagnostic payloads. Do not compare away known invalid historical state or claim a new model strategy result.
- [x] Run focused native/Python/paid regressions, independent review and Linux CI. Document the invalid trial and repair evidence; commit/push source only.
- [x] Only then resume representation diagnostics or new model decisions on a clean reproducible state. Existing frozen decision-3 artifacts may be polluted by preview leakage and are not a trustworthy counterfactual evaluation baseline.

Independent source review confirmed the cursor is the only changing static
allocation state in this module. The table `DEFAULT_PRIORITY` is only read;
non-water scratch arrays are automatic locals. Every historical action/reward
matches, with differences confined to worker assignment on fountains 17/21 and
fountain flags on houses 9/10. A controlled scarcity regression must still prove
the cursor is the sufficient cause. Reset initialization belongs before scenario
loading so an initially populated scenario runs its normal loader with a fresh
cursor; GUI load behavior is not changed.

## Repair Evidence

Missing cursor symbols first failed the native fixture compile and the Python
boundary test. Paid RED on the original DLL reproduced the divergence without
model calls: baseline `preview-replay-control_f5c13786` versus forecasts
`preview-replay-control_5c038999` differed in buildings/water/housing.

The minimal repair preserves the allocation traversal/arithmetic and normal GUI
cursor lifetime. Native scarcity tests pass under the canonical build, including
old incomplete rollback producing different assignments, full cursor restore
reproducing every city/building byte, bounds, full employment and zero workers.
Five locally runnable native fixtures pass; policy-blocked water/housing
executables remain unchanged. Linux CI is pending push of the seventh fixture.

Paid GREEN baseline `preview-replay-control_95c5aede` and forecasts
`preview-replay-control_c6e8a835` match all 12,800 actions/rewards and six endpoint
payloads, population 76 and victory state. Both episode resets start cursor 1.
Independent `replay_80b3b7cd` also strictly matches the forecast-control bundle.
This isolates the cursor omission as the sufficient cause of the reproduced
drift, not a successful strategy or a new model-selected run.

Review additionally found failed mission loading could leave the reset cursor
changed. The prior cursor is now restored on both loader-error paths; a missing
custom-map test observed the failing cursor change before the fix and passes
after rebuilding. Nested snapshots and repeated restore also pass. No standard
save-format, observation/action ABI or GUI load behavior changes. A final paid
rerun adds immediate cursor equality around each normal forecast generation.

Final precommit paid control under the rebuilt error-path fix: baseline
`preview-replay-control_1db08036` and forecasts
`preview-replay-control_e46cc3f1` match all six endpoint payloads, population 76,
victory, all 25,600 combined step messages/rewards and both reset cursors 1.
Immediate cursor checks pass 16/16 around full candidate forecasting. Both
manifests finished without artifact errors. Nested/failed-reset boundary tests,
47 planner units, six finance-feedback, six housing-feedback, seven replay,
five water-geometry and two artifact tests pass. Independent source review has
no remaining blockers. The transient compiler assembler-launch failure on the
first parallel build did not recur with the same toolchain at parallelism 2;
no toolchain or Windows policy changes were made.

## Committed Verification

Repair `1bd2d83e` was pushed excluding staged models/generated artifacts.
Linux [Headless Gym Tests run 43273641565](https://github.com/Iain-S/brutus/actions/runs/43273641565)
passed configure, all seven fixture builds and native CTest; queued graphical
builds are separate. The canonical DLL was rebuilt at this commit. Independent
`replay_f7574b50` matched all six payloads from final forecast control
`preview-replay-control_e46cc3f1` at 12,800 ticks, population 76, no victory.

Fresh model-selected `planner-local_43337274` ran on `1bd2d83e` after these
checks, using unchanged model/settings/budgets from the invalid trial. It
accepted 16 choices with no retries/fallbacks, reached 12,800 ticks/population 76
and no win. Its own strict `replay_0c5dc348` matches every step and all six final
endpoints. No old invalid benchmark has been relabelled valid, and no recorded
choices were imposed as policy. Repeated unproductive choices persist in the
clean run; subsequent non-executing probes are documented in the context plan.

## Residual Scope

A follow-up static-state audit found no other proved omitted cursor in the
reviewed peaceful population/culture/figure paths. It did identify a conditional
future risk: the granary GETTING-mode donor cache is refreshed on load rather
than restored at its original phase. That mode is not controlled by today's
planner tools and is not implicated in this trace. Before exposing it, test a
donor-stock threshold crossing between scheduled cache updates and restore;
do not claim this 12,800-tick control proves all possible eight-year states.
