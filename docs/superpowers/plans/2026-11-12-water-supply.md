# Normal Water Infrastructure

> **For agentic workers:** Execute inline with TDD and one final review; preserve user staging and existing IDs.

**Goal:** Remove the well-only housing barrier through actual native reservoir/aqueduct/fountain supply, not changed house requirements.

**Architecture:** Append reservoir/aqueduct IDs 59/60 (count61). Reservoir
coordinates are top-left; map to the GUI draggable-reservoir mode with the same
start/end center, so it places only one 3x3 structure at normal cost. Aqueduct
steps place individual native-validated tiles. Add read-only versioned water
diagnostics, Python binding, snapshot-composed water proposals, factual model
feedback and strict optional final-water replay. Use existing normal fountain
action29, staffing, supply ranges and simulation updates.

## Rulings

The user delegated implementation, not a hand-directed winning strategy. Choose
explicit ordinary actions over direct terrain writes or free infrastructure.
Independent source audit confirmed midpoint reservoir connectors and one-tile
aqueduct placement/charging. Retain menu gating, native routing and footprint
bounds. Action IDs0-58 and observation/config struct layouts stay fixed; expanded
RL action spaces need matching builds or migration. Work in the existing branch
and preserve staged models. Queries must not recalculate water supply or mutate
map caches. No renderer substitutes or automatic screenshot claims.

## Steps

- [x] Add query/native-action and placement regressions; observe missing API failures.
- [x] Implement native actions/query and Python binding; verify prices, footprint, supplied/dry infrastructure, buffer guards and immutability.
- [x] Compose bounded reservoir/fountain supply and midpoint aqueduct routes in snapshots; add optional planner proposals/feedback without a forced order. Verify normal activation and house fountain access.
- [x] Export final.water_supply.json and strictly replay when present; keep older bundles compatible.
- [x] Run focused native/unit/asset-backed tests, independent paid-action replay, review, document remaining evolution/prosperity limitations, commit and push source only.

## Validation

Use the canonical training environment and original assets from local settings.
Native fixtures may set isolated test data; asset-backed control must pay all
costs and advance only logged steps. Test dry/wet state, aqueduct continuity,
construction errors, snapshot rollback and independent replay. Placement is a
conservative bounded heuristic: actual native legality and forecasts decide
whether a proposal is usable; do not weaken map/game rules to make it fit.

## Evidence And Rulings

The first asset-backed run failed on the missing water API; geometry, model
feedback, forecast and artifact/replay regressions also failed before their
implementations. Initial paid reservoir/fountain access passed. The expanded
control confirmed dry relay -> supplied relay through actual aqueduct tiles,
and normal rejection of duplicate/edge/water-tile construction.

An evolution assertion initially failed despite water: a read-only native replay
inspection found fed, fountain-served houses below native desirability thresholds
(e.g. -6 versus -5). The control fixture now also pays for landscaping; it does
not alter model data or add a forced policy. Normal level4 evolution is observed.

Fresh review found a P2 diagnostic error: aqueduct grid values are multiplexed
topology/flow storage. Natural isolated aqueduct construction reproduced false
wet reports. The regression failed before the query was corrected to the native
wet image-band predicate. Review confirmed this read-only fix and no other
blockers. The C fixture was expanded to distinguish raw topology from wet images.

The corrected 12103-tick control `water-capability_64c437dd` reached118 people
and max house level4. Strict independent replay passed all existing checks plus
full water diagnostics. The pre-water imperial control also replayed unchanged,
correctly reporting `water_supply_verified: false`. Tests passed:42 planner,
5 geometry/feedback,5 replay,2 artifacts; all6 existing asset-backed regressions.

Windows Application Control blocks the newly linked C water fixture even outside
the sandbox. Do not disable/bypass that policy or claim the updated C fixture
ran. Existing C fixtures pass; native Python/game-API regression and replay are
unaffected. The updated C fixture compiles but remains a local execution gap
pending policy-administrator approval/signing. A transient launch failure also
affected a freshly linked imperial fixture, then cleared without source changes.

Ruling: add a separate read-only-token, asset-free Ubuntu headless CI job to
exercise all C fixtures independently without game data, models or Windows-policy
changes. Local PyYAML is unavailable; do not install parser dependencies into the
training environment just for the workflow. Hosted workflow validation/results
remain pending until observed after push. Next capability is house-demand/
desirability visibility and elective improvements, not another partial trial
with hidden evolution blockers. Citywide prosperity25 is still unproven.

## Committed And Hosted Verification

Source `3ace9ecd18892388d0f2f0850d17f1c926aa2eeb` was pushed, preserving the
user's staged models. Committed paid control `water-capability_5f241867` repeated
12103 steps, reached118 residents/max house level4 and retained a standard save.
Independent `replay_efe09063` passed messages/rewards, population/victory,
buildings, food, imperial and full water diagnostics. No model calls or edited
rules were used, and the fixture is not an autonomous win.

Public GitHub Actions metadata for
[run43212781327](https://github.com/Iain-S/brutus/actions/runs/43212781327)
confirmed that exact source SHA and successful configure/build/native-test
steps in the Linux `native-tests` job. All four asset-free native fixtures are
therefore independently verified, including the revised wet-image/topology
regression. Workflow static review found no correctness/security blockers.
The Windows executable remains subject to local Application Control; do not
change that policy as part of this feature. Obtain policy-administrator approval
or signing before retrying the local executable if local CTest execution is
needed. The game/Python integration and CI evidence remain valid independently.
