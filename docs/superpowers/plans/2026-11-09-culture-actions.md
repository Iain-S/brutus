# Peaceful Culture Candidates Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove the culture-action vocabulary ceiling without imposing a build order.

**Architecture:** Extend existing well-district proposals with schools, libraries,
theaters and actor colonies using existing C construction actions and footprint
sizes. Keep snapshot legality previews, costs, budgets and model choice unchanged.
Add factual theater/actor prerequisites and current culture-service counts to
the model context. This does not guarantee complete mission reachability: housing
placement, food delivery and other rating requirements remain separate.

**Tech Stack:** Existing Python planner, native Julius construction API and local command adapter.

**Spec:** The architecture and constraints in this plan.

## Global Constraints

- No new combat candidates or modified campaign rules.
- No forced action, scripted culture-first policy or free execution ticks.
- Preserve the four-district proposal cap and bound every macro to 128 actions.
- Keep the current branch; preserve staged user artifacts and commit explicit source paths only.

## Review Focus

- Actor-colony footprint must match engine properties.
- Unavailable or blocked culture construction must stay explicitly unavailable.
- Culture counts describe buildings, not guaranteed shows, staffing or coverage.
- Larger candidate sets must fit the model context in the bounded live trial.
- New previews must preserve independent action-log replay.

## Tasks

- [x] Add a failing proposal-vocabulary test and engine construction test.
- [x] Add four optional district candidate kinds and factual prerequisite context.
- [x] Verify construction, counters, preview rollback and observed culture progress.
- [x] Run a fixed local-model trial; independently replay and report limitations.
- [x] Review, document, commit and push verified source changes.

## Evidence And Rulings

The engine test constructs one of each culture building through normal paid
actions, checks preview rollback and counters, and observes culture 60 after
4800 ticks in the starter settlement. It does not execute a model policy or
demonstrate mission victory.

Ruling: add actual culture to the optional forecast alongside population and
food metrics. Otherwise the new actions' relevant forecast effect is omitted.
A unit test reproduced the missing field before implementation; no strategy
ranking or action filtering is added.

The fixed follow-up used 16 accepted decisions, no fallback, 12800 ticks,
340 residents and 60 residents holding food. It built no culture buildings;
executor capability and model competence are separate results. Its independent
replay passed, and prompts peaked at 2743/4096 tokens. Review found no confirmed
correctness defects; the requested suffix comparison and three-way inhabited
regression both pass. Unit tests include 25 planner tests plus two replay tests;
the asset-free CTest and focused native construction checks also pass.
