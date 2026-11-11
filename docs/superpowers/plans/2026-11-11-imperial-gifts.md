# Lawful Imperial Gift Capability

> **For agentic workers:** Execute inline with TDD; preserve staged model artifacts and existing action IDs.

**Goal:** Let an autonomous planner observe personal finances and choose native imperial gifts without modifying mission rules.

**Architecture:** Extract a pure fresh-cost helper from the existing emperor
calculation. Add read-only versioned imperial JSON, Python binding, and three
appended normal step actions. Execute the same native selection/payment/gift
functions as the GUI, retaining normal diminishing returns. Add optional model
candidates, favor/personal-savings forecasts and strict final-state artifacts/
replay. Treasury and personal savings must remain distinct.

**Tech Stack:** C headless library, ctypes, existing JSON planner and unittest/CTest.

## Rulings And Scope

The user delegated continued implementation without human-directed strategy.
Prefer ordinary paid step actions over a separate side-channel: existing action
logs/replay and tick accounting remain authoritative. Append IDs 56-58, leave
0-55 intact; observation/config structs stay unchanged. Action-space size grows
from 56 to 59, so old fixed-action-space RL checkpoints require their old build
or explicit migration. Do not alter or commit any such model artifacts.

No free savings, reduced costs, bypassed gift penalties, forced gifting policy,
combat or automatic request dispatch. Gift availability alone does not prove a
complete mission is winnable. Independently audit housing/prosperity coverage.
Keep the current worktree/branch to preserve user staging and installed build.

## Steps

- [x] Add native/integration regressions and observe failure on missing APIs/actions.
- [x] Implement fresh read-only costs/query and normal guarded gift step actions; test affordable/unaffordable gifts, personal vs city money, diminishing returns, buffer safety, unchanged IDs and query immutability.
- [x] Add Python binding, planner choices/factual inputs/forecasts; test preview rollback, natural salary funding, ordinary step accounting and independent replay.
- [x] Save final imperial diagnostics in future bundles and strictly compare when present; retain compatibility for older bundles lacking the file.
- [ ] Build, run focused suites/native tests, review, document audit limitations, commit and push source only.

## Validation

Use the dedicated training interpreter/library and original game data from
ignored local configuration. Native fixtures may set state only inside tests;
asset-backed integration must earn savings through normal simulation. Test
snapshots against independent action replay, and retain a final standard save
for any bounded end-to-end run. No new model download or live model benchmark
is needed for this capability checkpoint.

## Evidence And Rulings

Tests first failed on missing native header/API, Python binding, planner choices,
imperial model input/forecasts and artifact/replay support. The first integration
then exposed the old executor assumption that every action ID above housing is
construction: legal gift messages were misclassified as failure. A regression
failed before the narrow success-prefix correction and passes afterward.

Three native Gym tests, 41 planner unit tests, four replay tests and two artifact
tests pass. Native gift fixtures cover all three exact affordability boundaries,
city-vs-personal payment and lavish gains 10/5/3/1/0. The native integration earns
200 savings from salary, previews all gift sizes, checks business-state rollback,
pays two modest gifts for +3/+1 favor, waits 12 normal months and verifies +3
again. Its 29443 paid ticks are not an autonomous mission run. No money/favor
was injected into that integration test; native unit fixtures are isolated.

Independent action replay after previews matched strict imperial/food/building
diagnostics. A pre-feature 12800-tick trial also replayed unchanged, correctly
reporting `imperial_state_verified: false` for its absent historical file.
Baseline, food macro, culture macro, food-query and nine-block housing native
regressions pass. Fresh source review found no blockers. Minor residual coverage:
JSON rollback assertions exclude GUI-only selected/cached/rotating gift fields;
source serialization retains them and actions refresh prices/selection normally.

The parallel audit and read-only loaded-model inspection confirmed another hard
gap: well-only houses contribute at most 20 prosperity, below active target25.
Level4 contribution25 requires fountain water but not pottery. Normal supplied
reservoirs/fountains (and aqueducts where needed) are missing from the action/
planner vocabulary. Next implement real water infrastructure and test activation,
housing evolution and prosperity; do not substitute rule changes or a forced
winning policy. Scalable service siting and fiscal controls remain audit items.
