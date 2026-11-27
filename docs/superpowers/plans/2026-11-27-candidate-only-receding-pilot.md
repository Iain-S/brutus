# Candidate-only, Host-bound Receding Pilot

Start again from the verified actual 16000-tick food-supply state. The rejected
two-field pilot remains failed and unchanged; its candidate is not reused.
This is a new protocol with new inference calls, not filling a missing field.

## Contract And Host Binding

The output tool requires exactly one candidate_id from the entire legal root
domain, forbids extra keys and coercion, and never accepts thinking as an answer.
The host owns decision_id. Each worker receives a host context containing the
decision ID, native fingerprint, base-state digest, prefix digest and forecast
inventory digest. Before HTTP transport it saves a binding between that context,
the prepared prompt/enum and the actual outbound request SHA-256. The host
verifies all of those against its expected in-memory context, raw request,
receipt, strict typed/raw answer and unchanged current native fingerprint.
No action executes from a stale context or an unbound response. Native Candidate
freshness and exact forecast trace checks remain additional gates.

Model reply metadata is not silently synthesized: the one-field model output
stays separate from host-owned identity. Unexpected decision_id in a reply is
an extra-field failure under this new contract. The prior missing-field reply
remains invalid under its own two-field schema.

## Fixed Bounds

Keep the preceding pilot's sparse native tables, field aliases, system prompt,
source prefix and all legal choices. Preview every root for 800/1600/4800 ticks,
with full monthly diagnostics and independent reset/prefix replay per branch.
Reuse the first prepared state only after matching its base/prefix, regenerated
complete action domain, replay proof and pinned forecast inventory digest:
`36def399a9022538302237d64497df0ac88340bd3719dade92a69c8fbed859a0`.

At most three decisions, each with original/reversed/original calls. Require
three valid agreeing outputs and exact original-order request repetition; no
vote or preferred-answer fallback. Execute only 800 ticks before regenerating
all forecasts. At most nine new model requests; stop on schema/transport/context
failure, disagreement, stale binding or replay mismatch, with no repair/retry.

Keep pinned instruct weights/defaults and Pydantic AI versions, seed 20261122,
temperature .7, top_p .8, top_k 20, min_p 0, num_ctx 8192, max_tokens 256,
effort=none and a 170-second killable worker deadline. Accept only complete
tool-call finish and prompt headroom of 256+128. Use/remove one unique verified
temporary alias. Max native episode ticks 40000 is only an administrative cap;
new actual budget remains 2400. No native rule, population cap, score, winning
sequence, production dependency or normal planner behavior changes.

## Work And Verification

- [x] Create new ignored candidate-only transport/pilot/audit helpers, preserving
  old sources and evidence. Keep request/model/host metadata clearly separate.
- [x] Dry-run A/B/A typed HTTP with the full 34-root table, independently decode
  all fields, verify exact repeat bytes and test malformed replies plus stale,
  missing or tampered host/request bindings before any live action.
- [x] Obtain a fresh read-only code review under the requesting-code-review
  skill; resolve material findings with regression checks. Commit this protocol
  before inference. No repeated approval is needed for autonomous continuation.
- [ ] Execute the bounded pilot and preserve all failures/partial traces; audit
  schema, receipts, native bindings, model identity, forecast/delivery and cleanup.
- [ ] Independently replay actual native trace, retain real saves/six diagnostics,
  report outcomes/tradeoffs/limits and commit/push docs. Preserve unrelated
  BRUTUS.md and the user's staged models; generated artifacts stay ignored.

## Interpretation

This tests usability of a smaller output contract with equivalent host freshness
protection on an expanded state. It cannot prove that the contract alone causes
better choices, universal schema compliance or a strategy win. Original/reverse
plus one repeat is not a full permutation study. Future preview points become
counterfactual after replanning; only the delivered interval must match its
selected forecast. A win still requires sustained native multi-goal progress.

## Ledger

Ignored files: `runs/candidate_only_transport.py`, `runs/candidate_only_pilot.py`,
`runs/audit_candidate_only_pilot.py` and `runs/check_candidate_only_protocol.py`.
Old two-field sources and their failed record are unchanged. Host dispatch IDs
are unique per worker and stay outside model requests, so repeated A bodies
remain byte-identical while replayed/stale dispatch bindings are rejected.

Validation archive:
`runs/candidate-only-validation/20261127T095646.676598Z/`.
Ten offline tests pass: typed one-field/full-domain output, exact A bytes with
distinct bindings, wrong decision/forecast/native fingerprint, missing/tampered
bindings/requests, extra host metadata, invalid/duplicate roots, incomplete or
unsafe telemetry and thinking-only output. All three mocked HTTP calls are
synthetic; no game environment or model generation is used. Independent table
audit decodes all 2346 native cells per request and validates every emitted
schema/request/binding. Installed dependency `pip check` and compilation pass.

Fresh read-only code review reports no material findings. It checks schema,
host/dispatch/request identity, native fingerprint/base, agreement and delivery
gates. Independent actual trace replay remains required after any real action.
