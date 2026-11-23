# Instruct ToolOutput Frozen Order Follow-up

Continue the user-authorized ToolOutput spike before considering integration.
Use the existing ignored Pydantic environment and pinned native order archive.
No live planner, training dependency, native environment or historical helper is
changed. Keep unrelated staged models and BRUTUS.md untouched.

## Predeclared Schedule And Gates

Maximum eight model calls: the first six conditions of the old order schedule
(three cyclic orders, two states, alternating state order), then exact repeats
on states 3 and 2. Orders are compound/single/wait, single/wait/compound and
wait/compound/single. Each alternative occupies every position once per state.
The three reverse orders are untested; this is smaller than the old full sweep.

Retain the pinned instruct weights/template/defaults, seed 20261122, temperature
.7, top_p .8, top_k 20, min_p 0, context 8192, max_tokens 256, effort=none and
170-second killable worker deadline. One unique temporary alias holds the three
compatibility settings, with its weight blob, parent and defaults independently
verified and alias removed afterward. No download or thinking-model calls.

Use Pydantic AI ToolOutput, one select_candidate output tool, strict client
validation and no agent/SDK retries; at most one HTTP request per worker. Dynamic
decision_id literal and candidate enum must match each declared condition.
Only native comparison row order and output enum order vary across orders;
system instructions, labels and values remain fixed. JSON body bytes of exact
repeat controls must match. Stop after any invalid output, timeout or receipt
failure; no repair or budget change.

Schema validity, repeated-control agreement, presentation consistency and
strategic quality are separate gates. Compare only the matching six historical
ID-only conditions from the pinned old archive, not its full twelve-call block.
The old answers are historical observations, not fresh interleaved controls.
Chat formatting, endpoint, tool schema and alias differ: no isolated library
effect, general superiority, latency improvement or campaign progress claim.

## Execution

- [x] Create ignored runs/tooloutput_order_followup.py from the audited spike,
  generalizing only decision/enum order and adding the bounded schedule.
  Preserve the old runner and all old archives. Fix empty DELETE parsing in the
  new runner only. Record source snapshots, exact dependencies and inputs.
- [x] Run synthetic HTTP through all eight scheduled conditions to verify
  dynamic schemas, exact request controls and no native initialization. Recheck
  thinking-only/invalid/extra-field rejection without retries.
- [x] Inspect the complete emitted dry-run requests against frozen inputs;
  commit the protocol before inference. Run at most eight sequential calls.
- [ ] Independently audit raw accepted/failed evidence, request schedule/body
  equality, counters, model/alias/reference identity and cleanup. Withhold
  positive gates on missing or contradictory evidence; preserve failures.
- [ ] Record outcomes, limitations and next useful work; commit/push docs only.

## Ledger

This remains an empirical spike, not a production migration. Four synthetic
failure checks and complete request inspection are appropriate; no new training
tests or broad suite rerun is needed without production changes.

All eight synthetic HTTP conditions pass; separate thinking-only, invented-ID
and extra-field cases are rejected with one simulated request each and no retry.
Dry-run archive:
`runs/planner-input-probes/2026-11-23/20261123T145035.147748Z_tooloutput-order-dry_6be511fd/`.
Independent `runs/audit_tooloutput_order.py` inspects every full emitted request,
exact native transformation, dynamic schema, raw/typed match, receipt and repeat
body bytes. The dry-run audit passes without model calls. Installed dependency
`pip check` passes. Source/helpers and audit code are copied into local archives.
