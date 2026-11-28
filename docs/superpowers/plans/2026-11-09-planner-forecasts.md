# Planner Forecasts Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expose optional engine-generated outcome forecasts without choosing a strategy for the model.

**Architecture:** Preserve construction-only legality previews and add a separate bounded no-action continuation inside the same snapshot. Include a compact forecast in candidate JSON; do not change executable macro actions or charge hypothetical ticks to the live episode. Continue in the existing checkout and branch to preserve the ongoing local trial and the user's staged artifacts.

**Tech Stack:** Python, Gymnasium, the headless Julius shared library, local Ollama command adapter.

**Spec:** The forecast design and constraints below.

## Design

`--forecast-ticks` defaults to zero (disabled), with an upper bound of 8,000.
It requests a minimum total preview duration including construction, clamped to
the remaining episode budget. Forecast all usable candidates including waiting.
Report actual forecast ticks, outcome status, population, treasury, food stocks,
residents with food, health and farm staffing. Loss or truncation during the
continuation is evidence to report, not a reason to hide a legally buildable
candidate. A forecast is a single no-further-construction continuation, not a
prediction of future model decisions or a long-term viability guarantee.

## Global Constraints

- Restore all speculative state, including on exceptions.
- Keep legality, construction outlay and forecast outcomes distinct.
- Do not change model adapter configuration during the active comparison trial.
- Preserve staged models; commit source files explicitly.

## Review Focus

- Forecasts near the episode budget must not step beyond it.
- Victory or loss during continuation must stop simulation immediately.
- Failed construction must not receive a misleading successful forecast.
- Disabled forecasts must preserve the existing JSON behavior.
- Engine previewing must not change independent replay results.

## Tasks

### Task 1: Bounded engine forecasts

- [x] Write unit tests for rollback, failure, budget and terminal outcomes; observe failure before implementation.
- [x] Add forecast helper and optional decision-context argument in `python/julius_gym/planner.py`.
- [x] Add an engine regression comparing forecasted and actual continuations and restored state.

Task 1 evidence: eight boundary unit tests pass. The engine test forecasts a
food-district continuation, reproduces it through charged execution, checks
rollback, and clamps a requested 8000-tick forecast to 1400 remaining ticks.
The inhabited snapshot regression also passes after the preview refactor.

### Task 2: Runner and local adapter

- [x] Add validated CLI option to `python/examples/run_planner.py` and compact optional forecast columns to `python/examples/ollama_planner.py` after the unchanged trial finishes.
- [x] Extend adapter tests, document semantics, run focused and engine tests.
- [x] Run a bounded forecast-enabled local trial, independently replay it, and report results without claiming strategic competence.
- [x] Review source diff, commit and push verified changes only.

## Review Ledger

The read-only reviewer found transient annual wind and victory/force-win flags
outside normal saves. Both failures were reproduced before fixes and addressed
in commit `31ecd5a8`; native boundary tests pass. The reviewer reported no new
correctness findings after those fixes and adapter wiring. Follow-up coverage
also checks restoration of a force-win flag already set before snapshot capture.

The unchanged eight-decision trial finished before adapter edits: 6400 ticks,
245 residents, eight accepted choices, zero fallback, no food supply and no win.
Its independent replay matched. This is execution evidence, not a claim that
the small model plans effectively. The forecast-enabled trial is separate.

The forecast-enabled three-decision trial also independently replayed: wait,
housing, housing; 2400 ticks, 49 residents, three accepted decisions, no fallback,
no food supply and no win (run suffix `planner-local_511a20f1`). It took about
24.7 seconds previewing and 243.9 seconds in inference. Forecasts alone have not
demonstrated improved strategy.

Ruling: restore the engine's initial wind on Gym episode reset as well as
snapshot rollback. A focused test showed a previous episode's wind survived a
fresh mission reset. This is a headless reset isolation fix; normal graphical
game behavior remains unchanged.

Final verification: 24 planner boundary tests plus two replay unit tests pass;
six asset-backed checks pass (snapshot boundaries, forecast engine, inhabited
preview equality, planner engine, food macro and baseline). Both live trial logs
independently replay with the final library. Source changes are committed using
explicit paths, excluding all preexisting staged model artifacts.
