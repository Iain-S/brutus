# Planner Context Budget

> **For agentic workers:** Use executing-plans and test-driven-development; freeze source during live trials.

**Goal:** Verify intact planner input before interpreting another named-forecast trial.

**Architecture:** Add adapter `--context-tokens` (2048-16384, default 4096),
forwarded only to Ollama `num_ctx`, already present in audit metadata. Preserve
all prompts, candidates, schemas, model modes, sampling and game behavior.

**Tech Stack:** Existing standard-library adapter and unittest suite.

## Ruling

Prior server logs prove six named-forecast prompts exceeded 4096 tokens.
Increasing explicit capacity is preferable to silently dropping candidates or
adding a hand-coded strategy. Retain defaults; choose 8192 for this experiment.
This is a configuration change, not an established strategic improvement.
Use the existing branch/workspace and preserve the user's staged models.

## Steps

- [x] Observe new tests fail: explicit/default compatibility, CLI forwarding/audit and invalid bounds rejected before inference.
- [x] Implement the option; pass planner tests, review and commit/push source only.
- [x] Preflight three large saved contexts at 8192, retaining requests/responses, runtime identity, prompt counts and truncation logs. Require completed valid choices, GPU offload and at least the 256-token output budget plus 512 spare tokens.
- [x] Run 16 decisions/12800 ticks with the prior objects-mode settings except context 8192. Keep adapter/executor frozen; independently replay all final diagnostics and record outcome, timings and headroom.
- [x] Record limitations and the next checkpoint; commit/push documentation without artifacts.

A larger context can increase memory use and wall time. If preflight exceeds
the existing HTTP/command limits, report the blocker instead of silently
changing timeouts. Prompt counts plus server logs are evidence for these
specific inputs, not a universal input-length guarantee.

## Implementation Evidence

The default/explicit request and CLI forwarding tests failed on the missing
keyword/flag. Invalid-bound tests specifically required the new range error,
not merely rejection of an unrecognized flag, and failed before implementation.
All 39 planner tests pass after the minimal option/validation change. No native
code, simulation or action vocabulary was changed.

Independent read-only review found no blockers. Its minor endpoint-acceptance
test gap was addressed by exercising CLI budgets 2048, 8192 and 16384; all 39
planner tests still pass. Source-only commit/push is the gate before live play.

## Preflight Evidence

From `planner-local_b502c162`, the three largest serialized prompt byte lengths
selected decisions 12, 10 and 14. At 8192 context, their actual prompt counts
were 4204, 4188 and 4158, leaving 3732, 3748 and 3778 tokens after reserving
256 output tokens. Responses completed within the unchanged 170-second HTTP
limit (41.3, 30.2 and 30.5 seconds). Current-decision JSON and listed candidate
IDs were validated; no game actions were executed.

The installed instruction-model digest matched the prior pinned manifest.
Loaded runtime capacity was 8192 with GPU offload, and the server logged no
prompt truncation. Complete requests/responses and runtime/native-library
identity are retained in ignored `runs/context-8192-preflight/`. Choices are
preflight observations, not a strategic-quality acceptance test.

## Trial And Replay Evidence

Source `894e216f`; run `planner-local_2c28aa7a`; replay `replay_01b87cea`.
16 accepted decisions, zero fallback, 12800 ticks, 140 residents, culture 40,
70 food-holding residents, no win. Household/market inventories were 259/404
units, granaries empty. Eight schools were selected and no general housing
expansions. Peak prompt 5098 of 8192, leaving 2838 after reserving 256 output
tokens. Runtime capacity/GPU offload verified, pinned model/native-library
identities unchanged, no server truncation entries. Source remained frozen.

Preview 129.6 seconds, inference 383.2, total wall 515.8. Strict independent
replay passed including full food diagnostics. Saves and runtime records are
retained in the normal ignored run bundles; no PNG was generated. Fresh unit
verification passed 39 planner tests, two artifact tests and three replay tests.

Ruling: observed context failure is resolved for this trajectory, not arbitrary
future inputs or strategy quality. Do not infer causality from one stochastic
run. Source audit now takes priority over further model tuning: 12800 ticks is
too short for the normal peace goal, and the existing action vocabulary lacks
the imperial controls needed for normal favor management. Next expose legal
imperial observations/actions and audit full-mission reachability; no modified
ratings, free money, forced gifts or hard-coded winning build order.

A separate read-only native reset inspection confirmed all five criteria are
enabled, with goals 2500/45/25/30/70 for population/culture/prosperity/peace/favor
and initial peace/favor 0/50. Its record is retained under ignored
`runs/mission-reachability-audit.json`; it executed no game actions. Source
analysis finds a best-case eight annual updates for peace 30 and no current
peaceful action path to the gift/request favor gains. This makes imperial
capability work a prerequisite for a credible full-win experiment, not a model
tuning preference.

Independent source review confirmed the peace sequence and favor capability
gap, including other positive sources: below-rank salary is unavailable;
defeating Caesar grants favor only below 35; distant-battle gains require
unavailable military dispatch and are outside peaceful scope. No counterexample
was found. The next checkpoint must audit every active goal, including housing
evolution/prosperity, before treating imperial controls alone as sufficient for
a full win. Result documentation is committed/pushed separately from artifacts.
