# Frozen Planner Factual Grounding Diagnostic Plan

**Goal:** Determine whether the current local model can recover recorded game
facts before changing its action-selection policy. Continue the diagnostic
checkpoint accepted after `1fcdd0ad`; this is not a production planner feature.

**Scope:** Read-only model probes on decisions 5 and 7 from the verified
November 18 `planner-local_03ba650f`. No Gym environment, DLL load, game actions,
new native state or copied save. Keep all candidates, scalar values/types,
mission objective and game facts. Preserve staged models and historical runs.
Use the current authorized branch, canonical interpreter and installed pinned
instruct model. No server settings, model installation or gameplay changes.

## Hypotheses And Alternatives

The live explanations claim housing is absent in a populated city, inflate a
72-tick action to 782 ticks and describe more blocked houses as an improvement.
These could reflect difficulty reading positional candidate rows, difficulty
reconstructing baseline overrides, arithmetic errors, or explanations that do
not faithfully represent action selection. A greedy but factually competent
policy is also possible. Do not assume a particular explanation in advance.

Compare production positional candidate rows against explicitly named
candidate fields, keeping the existing absolute forecast overrides and actual
wait baseline in both. This isolates outer row labelling, not every aspect of
encoding. Full independent forecast objects would substantially enlarge the
input and confound the test with context capacity; changing model or strategic
instructions now would confound representation with policy.

## Protocol

- [ ] Verify model digest, source manifest and source-context identity. Build a
  throwaway ignored diagnostic script, not a deployed adapter option. Check
  exact conversion roundtrips, every candidate/order/nonforecast field, all
  twenty scalar projection values/types and independent factual oracles.
- [ ] Run two repetitions for each state and each layout (eight calls), with
  the same 8K context, 256-token output, existing instruct sampling and
  170-second API timeout. Alternate layout order within each state. No hidden
  retries, candidate selection, answer hints, rankings or game actions.
  Retain full requests/responses, token counts, termination details and errors.
- [ ] Score twelve integer factual answers exactly, including current
  population, housing/wheat construction durations, forecast duration,
  housing/wait/wheat projected populations, housing/wait blocked-house counts,
  wheat food stock and two housing-minus-wait differences. Expected answers
  come independently from the recorded native context, never from model text.
  No correct-value enums or expected answers enter the requests. Require
  complete exact-key/type responses and existing inference/headroom checks.
- [ ] Report extraction versus arithmetic errors separately, per layout/state
  and repetition; audit failures separately from wrong answers. State the
  limits of targeted tasks, two repetitions, stochastic sampling and changed
  output schema. A successful factual audit does not validate free-text
  explanations, action choices or a mission win. Review evidence, record the
  next checkpoint and commit/push source documentation only.

## Artifacts And Acceptance

Use `runs/planner-input-probes/YYYY-MM-DD/<UTC>_grounding_<uuid8>/` with
`native_execution: false`, `executed_choices: 0`, source-run/save references,
source hashes, requests, raw responses, per-call scores and an aggregate audit.
Do not fabricate a fresh `final.sav` or claim a screenshot/replay for this
input-only experiment; its source campaign already has a strict replay.
Use type-aware equality (booleans are not integer answers), explicit schema
checks and no numerical tolerance. Any rejected/truncated request is not an
accepted factual answer. Preserve failure evidence and do not relax guards.

The user has delegated continued investigation and requested this next
checkpoint. This small diagnostic uses the existing probe pattern; it does
not authorize deploying named candidates, changing planner defaults, adding
human build orders or promoting a profile. Implementation choices above are
the investigator's, not claimed as user-prescribed strategy.
