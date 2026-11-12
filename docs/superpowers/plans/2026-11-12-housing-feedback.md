# Native Housing Feedback And Elective Landscaping

> **For agentic workers:** Execute inline with TDD and final review; preserve staged model files.

**Goal:** Let the model observe native housing constraints and choose paid gardens without a forced improvement schedule.

**Architecture:** Add a read-only housing JSON endpoint: active house state,
cached house/tile desirability, raw inventories/services, current/next native
model references and goods/service predicate results. Reuse the existing engine
predicate through a const wrapper with local demand counters; do not call UI
evolution text or processing functions. Models are included once, not per house.
Add bounded factual summaries/forecasts, ordinary garden proposals, full final
housing artifacts and optional strict replay. Existing action IDs/count61 and
observation/config/building-query layouts remain unchanged.

## Scope And Rulings

The user delegated continued implementation, not a human winning build order.
Expose conditions, not a claim that an upgrade is guaranteed: population, timing,
merging and expansion/space rules also apply. Maximum-level houses have no next
model. Preserve all native thresholds and goods checks, including their quirks.
Garden proposals use existing paid action8, clear only legal vegetation and do
not add unnecessary roads or overwrite infrastructure. Four-tile batches are
repeatable optional tools, not population caps or automatic policies. Keep the
existing branch/workspace and preserve user staging.

## Steps

- [x] Observe missing query/helper/summary/provider/artifact failures in tests.
- [x] Implement native const predicate/query and bindings; test model guards, current/next distinction, cached desirability, raw services, immutability and buffer limits.
- [x] Add bounded housing feedback and garden choices/forecasts; test paid fixture improvements and snapshot rollback without changing native rules.
- [x] Strictly replay final.housing.json when present; verify older bundles remain compatible.
- [x] Build/run focused checks, source review, asset-backed control/replay and asset-free Linux CI; document limitations, commit and push source only.

## Validation

Use the canonical training interpreter/library and original data from ignored
local settings. Native fixtures may seed isolated models; normal integration
must use loaded original models and paid steps. No assets, run outputs or models
are committed. Keep Windows Application Control untouched; use the existing
asset-free CI workflow if a local C fixture is blocked. Preflight enlarged model
inputs before another live LLM trial; this checkpoint need not spend model calls.

### Evidence Before Commit

43 planner, six housing-feedback, six replay, five water-geometry and two
artifact unit tests pass. Six asset regressions (baseline, food macro, culture,
food query, nine housing blocks and imperial gifts) pass. Paid control
`water-capability_675ea034` reached level 4, 116 residents at 12,103 ticks;
`replay_8f440288` strictly matched all diagnostics including housing. Legacy
`water-capability_5f241867` replayed with the absent housing check correctly false.
No fixture or trial won the mission.

Native housing target builds; Windows Application Control blocks its execution.
Existing observation/food/imperial fixtures run locally.
Review identified signed negative house levels bypassing upper-bound validation;
both new entry points now reject them and the native fixture covers -1.

### Committed Verification

Implementation `167388ad` was pushed. Linux Headless Gym Tests run
[43246843495](https://github.com/Iain-S/brutus/actions/runs/43246843495) passed
configure, all five native fixture builds and CTest. This resolves the native
execution gap without changing Windows policy; graphical build status is separate.
Postcommit paid control `water-capability_3f869213` repeated level 4 at 12,103 ticks
with 116 residents. Independent `replay_d5ed0f61` matched all diagnostics,
including housing. Neither run won Tarraco. User-staged model files were excluded.
