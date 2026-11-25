# Bounded Receding Root Forecast Pilot

Continue from the actual 16000-tick model-selected food run, not a hand-picked
counterfactual. Pin its manifest, full primitive trace, final diagnostics and
delivery audit. Replay the prefix with the identical DLL before new actions.
Keep all native game/victory rules and the existing macro vocabulary unchanged.

## Bounds And Representation

At most three new decisions, each executing one model-selected root plus idle
to exactly 800 charged ticks before replanning. Preview every legal root at
800/1600/4800 ticks (one/two/six months), including construction time. Six months
exposes the delayed food effect previously observed at month 5; this is an
operational choice, not an established optimal horizon. Max episode ticks 40000
only permits previews beyond the current prefix; actual new budget is 2400.
Abort rather than truncate the domain if more than 64 legal roots appear.

Retain every existing forecast metric plus peace, labor available/needed/employed
and housing capacity. Encode common wait outcomes once per horizon. Root
overrides contain named **absolute** values only where they differ from wait;
omitted fields inherit wait, not zero. Decode and compare every full root vector
against native evidence before inference. Keep all root IDs, native victory
targets, calendar, macro metadata and unavailable reasons. Raw diagnostics/maps
remain archived; this is not a promise that the model reads every raw field.
The sparse encoding is lossless for the declared forecast fields, not a score
or a filter. This changes representation/cadence/horizon together, so no causal
comparison with the earlier single-state dense-table experiment is claimed.

## Selection And Execution Gates

Use the pinned instruct weights/template/defaults and existing isolated Pydantic
AI environment. Seed 20261122, temperature .7, top_p .8, top_k 20, min_p 0,
context 8192, max_tokens 256, effort=none, hard worker deadline 170 seconds.
No agent/SDK retries and at most one HTTP request per worker. Verify actual
raw prompt-token headroom of 256+128 before accepting an answer.

For each state, ask original A, reversed B, exact A repeat: up to nine calls
total. Move rows and tool enum together, preserve all other facts. Require all
three complete strict typed/raw answers to agree before execution. No majority,
preferred-action fallback, repair, raised budget or post-failure re-encoding.
Stop on disagreement, incomplete inference, unsafe context or integrity error.
Only A has an exact repeat; B is not repeated and other orders are untested.

Each complete root forecast restores the exact base, including six diagnostics
and map. Before model inference, independently replay **all** forecast branches
from reset and the actual prefix without candidate generation, checking all
monthly snapshots and primitive results. After selection, recheck legality,
execute only its first 800 ticks and match that forecast's primitive trace and
checkpoint. Later forecast points remain counterfactual after replanning.

Retain all partial actions on execution failure, real final saves, six final
diagnostics, actual/predicted checkpoints and model receipts. Independently
replay the final actual trace. Stop reasons and failures remain explicit; a
valid exploratory result does not establish global selector stability or a win.

## Tasks

- [x] Build ignored pilot/forecast-replay/audit scripts using existing native
  execution and strict ToolOutput transport helpers; preserve old runners.
- [x] Prepare first state's complete native forecasts without model calls or
  new policy actions. Verify round-trip sparse encoding and dry-run A/B/A plus
  rejection/gating checks, inspect full wire requests and dependency versions.
- [x] Commit protocol before inference; run at most three decisions/nine calls
  with every predeclared gate and complete per-case native branch replay.
- [x] Audit all requests, schemas, decoded native outcomes, counters, rollbacks,
  forecast/delivery matches, alias cleanup and independent final trace replay.
- [x] Record endpoints/tradeoffs/limits and useful next work; commit/push docs
  only, preserving unrelated BRUTUS.md and staged model files.

## Ledger

Source actual manifest SHA-256:
`e40d1819889db4c5877b1bf0a44e8600d01e1ae6100dc21d6c44db39f35846a4`.
Source 16000-tick trace SHA-256:
`e2dd11da4a35848d415fe0e55de977fbc42026bd2c591e2f2208ac23b488f887`.
The pilot also pins its source final checkpoint, six diagnostics and independent
delivery audit. No production integration, dependency migration or game-rule
change is authorized by this empirical pilot.

Prepared-state archive:
`runs/tarraco/2026-11-25/20261125T162026.256169Z_receding-root-prepare_ae1ddd2a/`.
The new state has 34 legal roots. Every 4800-tick forecast restores the exact
base; independent reset/prefix replay verifies all 34 branches and six monthly
checkpoints per branch in 141.0 seconds. Preparation executes zero new policy
ticks and makes zero model calls. Reuse the prepared case only after checking
base state, prefix bytes, complete regenerated action domain and replay evidence.

Field aliases are declared once and map to full native metric names. Independent
decoding checks all 2346 native cells per table (34 roots x 3 horizons x 23
fields), including added labor/capacity fields. A/B/A mocked HTTP calls pass
strict typed/raw validation and exact A request-body repetition. Separate raw
checks reject invented roots, float decision IDs, extra fields, length finishes,
unsafe headroom and thinking-only output. Pinned isolated dependencies and
`pip check` pass. First prompt length is 14651 characters; an alternative
tokenizer estimate is not acceptance evidence, so actual Ollama counts remain
mandatory. No inference-time re-encoding or domain filtering is permitted.

Current-state forecast data and replay reports are hashed before model calls and
rechecked before delivery. Preserve started-attempt records with unknown counters
if a worker dies before verifiable terminal evidence; retain partial primitive
execution in logs/saves on failure. The existing production planner is unchanged.

## Failed Outcome

Protocol commit `e298e441`; actual pilot:
`runs/tarraco/2026-11-25/20261125T162817.497333Z_receding-root-pilot_6845521d/`.
The first original-order response has a complete tool_calls finish, safe 6044
prompt tokens and 27 completion tokens. It returns only candidate_id, omitting
the transmitted schema's required decision_id=5. The candidate name is in the
legal domain, but the answer is invalid. Pydantic AI rejects it with zero retries
permitted. One request/one received response, 64.1-second worker wall time,
neither deadline nor token cap exhausted. No B/A-repeat or later decision calls.

The pilot stops exactly at that gate, with zero new policy ticks/decisions and
preserved error status. Its 78.2-second run includes prefix reconstruction and
temporary alias setup/removal. Independent audit decodes all prompt values,
checks the emitted schema/argument omission, receipt/counter evidence, forecast
inventory, source hashes and model identity. It verifies a **failed** record,
explicitly pilot_passed=false; no output or strategy gate is promoted.

Full actual-trace replay:
`runs/tarraco/2026-11-25/20261125T163245.071332Z_receding-outcome-replay_47b4344c/`.
All 16000 primitive results, six diagnostics and base map/state match in 3.7
seconds. Replay retains source_experiment_status=error and source_pilot_passed=false.
Population 103, food coverage 57, housing level 2 and treasury 6503 are unchanged.
Final saves/diagnostics remain available; no new plot or screenshot is necessary
for a zero-action continuation.

The preparation, prompt validation and strict rejection checks pass. Adaptive
decision performance, new-state order stability and further goal progress remain
unassessed. No retry, output salvage, prompt repair, re-encoding, budget increase
or production integration follows. Next useful scope is a new candidate-only
output contract with host-owned decision/request/state identity and all current
validation/freshness gates; this failed two-field record remains unchanged.
