# Native Root Breadth And Horizon Diagnostic

Use the verified compound run's 6400-tick endpoint as a common base. Reconstruct
it from the pinned primitive log with the same headless DLL, matching every
message/reward and all six final diagnostics before creating any new branch.
No model calls, scored strategy ranking, hand-picked winning sequence or rule
changes. Existing planner code and all historical archives remain unchanged.

## Experiment

Enumerate the complete engine-tested legal root menu with existing
decision_context at radius 14, forecast_ticks=0, budget=9600. Include wait and
all legal control/gift/service/construction choices; retain unavailable reasons.
Abort if more than 64 roots rather than truncate/rank the domain.

From an outer snapshot of the same base, execute exactly one root macro then
idle without further construction up to 9600 additional native ticks. Checkpoint
every 800 ticks (12 checkpoints); primary comparisons are 800/1600/4800/9600.
Charge macro and idle ticks together, so comparisons with wait have equal time.
If a branch ends or fails early, retain actual ticks/status and do not fabricate
later checkpoints or treat it as an equal-time completed comparison.

The source episode cap was 8000. This diagnostic uses max_ticks=20000 solely to
permit base 6400 plus horizon 9600; native simulation and victory rules are
unchanged. This horizon crosses an annual update but does not establish the
multiple clean years needed for peace 30. It tests one-root-plus-idle forecasts,
not adaptive multi-step planning or an executed LLM policy.

Record each primitive action/result immediately, monthly scalar observations,
forecast fields, six raw diagnostics, real final branch saves and manual-review
notes. Restore and compare base observation, fingerprint and six diagnostics
after every branch and on exceptions. Export the restored base separately.
Do not label speculative branch ticks as delivered campaign-policy progress.

Independently replay every branch from a fresh reset and the pinned source
prefix, with no speculative candidate generation. Match all primitive messages,
rewards, terminal flags, monthly scalar observations and all six diagnostics.
Check maps at checkpoint boundaries as additional state evidence. Replay every
branch rather than selecting a favorable outcome. Preserve replay failures and
withhold forecast-reliability claims if any comparison fails.

## Files And Validation

- [x] Add ignored `runs/probe_root_horizons.py` using the canonical interpreter,
  explicit original data directory and DLL path, existing snapshot/execution
  helpers and the fixed source log. Pin manifest/actions/six diagnostics and DLL
  hashes, copy source evidence and executed helper snapshots into the archive.
- [x] Recheck DLL loading and prefix replay before root branching. Check complete
  root domain, every rollback, actual tick accounting and all diagnostic exports.
  This is an empirical diagnostic, not a production feature; its proof is native
  execution and independent primitive replay rather than mock training tests.
- [x] Commit this protocol before inference-free simulation; run at most 64
  roots, each at most 9600 additional ticks, preserving all failures.
- [x] Run independent replay over every recorded branch/checkpoint and audit
  source/record integrity. Retain branch saves, diagnostics, logs and replay
  report under ignored runs/tarraco/2026-11-24/.
- [x] Record useful endpoint/horizon differences and limitations in results/TODO;
  commit/push documentation only, preserving unrelated staged work.

## Ledger

Preflight DLL SHA-256 matches the historical compound run:
`0f87723c4f6190b44e20fecde86bc5fb133184bc98a3bd6304297fca0936863a`.
Source run manifest remains pinned as
`53ed8dd2b878bb82126158283b98cc777aabe6c1ad2fa6da7ca75b11f4c4d18f`;
primitive log as
`8977063597d5fc6300b6eae38d481c8f17475dd9f65d2ab75e218390c6d44a0d`.
The runner additionally pins the six original final diagnostic files. No new
policy choice or winning build order is supplied by this diagnostic.

## Outcome

Protocol commit `132dcbbd`; archive:
`runs/tarraco/2026-11-24/20261124T112429.900813Z_root-horizons_c39b0324/`.
All 20 legal roots in the existing bounded macro vocabulary complete 9600 ticks,
and all 20 snapshot rollbacks match the exact base. Three unavailable roots retain
their reasons. Enumeration takes 54.8 seconds. Separate reset/prefix/primitive
replay takes 75.9 seconds and matches every action message/reward/terminal flag,
all 240 monthly scalar/forecast/six-diagnostic payloads and map hashes.

Wheat supply takes 50 construction ticks and reaches population 103, food coverage
57, house level 2, farm workers 6, granary 100 and market 328 food units at year
end. Workers are first observed at month 3, food coverage at month 5; monthly
sampling does not establish exact onset ticks. There is no further construction.
School/library/theater reach culture 15/20/25 by month 1, so these particular
benefits do not need a longer horizon. Wait ends at population 42/food 0/culture
0/house level 1; it also gains prosperity 5/peace 2 at annual rollover. Treasury
and fountain-coverage tradeoffs remain explicit; no winner or weighted score.

The retained independent replay source/audit cover all branches, not a favorable
subset. Summary audit and all-root CSVs pass; selected trajectories are exported
as PNG/SVG using standard plotting tools and visually inspected. Every branch has
a real final native save, six diagnostics and manual screenshot-review notes.
The restored base is exported separately. No new game screenshot is claimed.

No model calls or new policy ticks; 192000 counterfactual branch ticks and 320000
independent replay ticks including prefixes. Native C/Python production code and
training dependencies remain unchanged. Next is a bounded experiment exposing
the complete native root forecasts to model selection, with explicit headroom,
presentation, legality, forecast/delivery and replay gates. This diagnostic does
not itself solve selection reliability or demonstrate a campaign policy win.
