# Campaign Planner Results

Updated: 2026-11-21. Latest model experiment: 2026-11-19.
Compound-preview source checkpoint: `3ce633ac`; earlier model checkpoint: `936cc933`.

## Objective And Current Approach

Find fast native wins in peaceful campaign missions, starting with Tarraco
(campaign rank 3, zero-based), without changing game rules, capping population,
or prescribing a human-selected winning build order.

The current experiment uses a local LLM to choose among legal macro actions.
Deterministic code constructs and validates those actions, simulates native
forecasts, executes accepted choices, and records results. It is not a trained
DNN reinforcement-learning policy. The model is
`qwen3:4b-instruct-2507-q4_K_M`, served locally through Ollama.

**No campaign win or demonstrated fast-win strategy has been achieved.**
See [remaining work](PLANNER_TODO.md) for the next checkpoint.

## Native Compound Preview Checkpoint: 2026-11-21

An additive `julius_gym.compound` interface now previews one or two named macro
steps, regenerating native-tested legal candidates in each successor state.
Plans carry no future candidate objects or action arrays. Initial state and
native observation freshness are checked; unavailable successors, construction
failures, terminal outcomes and exhausted budgets stop the plan immediately.
Construction and observation ticks share the actual remaining budget.

An outer snapshot restores the base on success, invalid successor or exception.
Each preview includes a wait control from that same base for the plan's actual
charged ticks. `plan.valid` and `equal_time` are separate gates: an invalid prefix
is not a valid plan and a control that ends early cannot support an equal-time
comparison. Raw per-stage actions, messages, rewards, tick counts, net treasury
changes, full scalar observations (including peace), staffing/food diagnostics
and all six final native diagnostic payloads are retained.

The following are fixed engineering fixtures, **not model proposals or strategy
evidence**. Both completed plans ran for 1,600 ticks, including an 800-tick
minimum cycle per step. The invalid plan stopped at 800 ticks; each wait control
used exactly its corresponding duration.

| Fixture | Status | Population | Fountain Residents | Treasury | Food / Culture |
| --- | --- | --- | --- | --- | --- |
| Housing, then successor water supply | completed | 42 | 42 | 7,708 | 0 / 0 |
| Wheat supply, then successor school | completed | 24 | 0 | 7,182 | 0 / 0 |
| Housing, then nonexistent successor | invalid_successor | 13 | 0 | 7,818 | 0 / 0 |
| Wait control, 1,600 ticks | completed | 0 | 0 | 7,984 | 0 / 0 |
| Wait control, 800 ticks | completed | 0 | 0 | 7,992 | 0 / 0 |

The wheat/school fixture still has zero farm workers, food inventory, food
delivery and culture at this horizon. Successful construction is not successful
staffing or service delivery. No native victory or strategic improvement is
claimed, and the live model command has not changed.

All corrected previews restore the native fingerprint, freshly read native
scalars and all six diagnostics. The plan's raw-action continuation then runs
directly from the restored base, without resetting or regenerating candidates;
this checks hidden-state rollback effects. Stage endpoints and final diagnostics
match predictions. Separate fresh-process `examples/replay_run.py` invocations
also match every action message/reward and all six final diagnostics for all six
archives. That is 8,000 independently replayed ticks across controls and prefixes.

Source-pinned evidence under `runs/tarraco/2026-11-21/`:

- Housing/water: `20261121T183154.823269Z_compound-control_d63f5bba/`;
  wait: `20261121T183155.415341Z_compound-control_a7c75678/`.
- Wheat/school: `20261121T183204.879826Z_compound-control_f3511cb6/`;
  wait: `20261121T183205.438715Z_compound-control_0caf8df1/`.
- Invalid successor prefix: `20261121T183215.374656Z_compound-control_925d4b0b/`;
  wait: `20261121T183215.731156Z_compound-control_a8f76d93/`.

Each archive contains `preview.json`, source snapshots/source and library hashes,
the actual trace, real `final.sav`, six final diagnostics, `REVIEW.md` and
`independent-replay.log`. Earlier dirty-source controls are retained as preliminary
evidence; the directories above pin committed source `3ce633ac`.

All 161 unittest cases pass, including 19 compound cases, 110 planner cases and
seven replay cases. Native forecast health and the compound controls pass;
`python -m pip check` reports no broken requirements. Full wildcard unittest
discovery was also attempted: seven existing CLI scripts fail importing without
their required path arguments and `test_import` fails printing Unicode under
Windows cp1252. The complete set of actual unittest-class modules passes. Exact
script names and fresh-review corrections are in
[the implementation plan](superpowers/plans/2026-11-21-compound-previews.md).

## Latest Native Run

Run directory, relative to the checkout:
`runs/tarraco/2026-11-19/20261119T105542.706780Z_planner-local_d54f5084/`.

- Eight accepted decisions, 6,400 native ticks, sixteen API calls.
- No retries, fallbacks, timeouts, or validation failures.
- Selected two housing expansions, three markets, one water-supply macro,
  and two landscaping macros.
- End state: population 56, fountain coverage 42 residents, health 50,
  treasury 7,234, favor 50.
- Culture, prosperity, peace, food stocks, food delivery, and tax income
  remained zero; maximum occupied housing level was 1.
- Stopped at the decision budget, not at a native victory.

Independent strict replay matched all 6,400 action messages and rewards and
all six final diagnostic payloads:
`runs/tarraco/2026-11-19/20261119T110723.972040Z_replay_a909eb19/`.
The full-prefix review and native save are in
`runs/tarraco/2026-11-19/20261119T110726.136443Z_planner-prefix-review_0a31f0cf/`.

The complete wheat-supply macro was legal at every decision but never queried.
Cultural-service macros were legal from decision 1 but never queried. Markets
are food-related, so this does not mean the model ignored every food tool.
These observations motivated the frozen full-domain experiment below.

## Latest Frozen Experiment

The final selection stage was allowed to choose any currently legal candidate,
not only candidates in its earlier two-item query. Four saved states were
tested under narrow and full-domain profiles, twice each: sixteen final API
calls, no new query calls, and no game actions.

| Saved Decision | Original Query | Narrow Choice, Both Repeats | Full Choice, Both Repeats |
| --- | --- | --- | --- |
| 1 | Water, Market | Market | Water |
| 3 | Water, Granary | Water | Water |
| 5 | Water, Market | Market | Water |
| 7 | Housing, Farmland | Housing | Housing |

All sixteen responses passed validation. None of the eight full-domain
responses selected an action outside its original query. Broader final access
works technically, but did not demonstrate broader exploration or better play.
This is a small, unseeded, frozen-context experiment, not a strategy benchmark
or a causal isolation of model capability, lookup anchoring, or planning depth.

Evidence:
`runs/planner-input-probes/2026-11-19/20261119T173520.971552Z_full-domain_ab0ae6bc/`.
Detailed protocol, audits, limits, and source validation are recorded in
[the completed experiment plan](superpowers/plans/2026-11-19-full-domain-selection.md).
The full-domain helpers have not been promoted into the live command.

## Verification And Limits

- The completed checkpoint records 110 planner tests and seven replay tests
  passing, plus independent source review. These are historical results, not
  a claim that tests were rerun for this documentation update.
- Native water-allocation cursor rollback was repaired and tested earlier;
  the latest native trial passes strict replay. This is not proof of
  determinism for every future compound rollout or multi-year campaign.
- Earlier failed evidence-quoting and timeout experiments remain failed gates;
  successful ID-only selection does not retroactively validate them.
- Tarraco targets population 2,500, culture 45, prosperity 25, peace 30,
  and favor 70. The 6,400-tick prefix cannot establish a win. Peace progression
  alone requires multiple annual updates under native rules.
- Native housing level 4 contributes prosperity 25 without requiring pottery.
  Missing industrial macros therefore do not by themselves prove that the
  prosperity target is unreachable. Actual staffing, food, evolution,
  finances, and annual ratings still need to be demonstrated.
- The native multi-step preview foundation is now tested as described above;
  model-proposed compound evaluation has not been implemented or run.

## Artifacts And Manual Review

Native campaign runs use
`runs/tarraco/YYYY-MM-DD/<UTC>_<mode>_<uuid8>/`, containing `run.json`,
`actions.jsonl`, real `final.sav`, six final diagnostics, and `REVIEW.md`.
Input-only model probes and command transcripts have separate directories.
Generated artifacts are local and ignored; repository documents retain their
paths so they can be located without committing game assets or run output.

Real-asset `final.png` review remains manual/pending using graphical Julius
and its screenshot facility. No automatically rendered in-game screenshot
has been established by these experiments.
