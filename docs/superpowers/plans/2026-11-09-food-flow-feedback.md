# Food Diagnostics And Feedback Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Let the local planner distinguish food production, storage and delivery observations without prescribing a build order.

**Architecture:** Add a separate read-only native JSON query for active food farms,
granaries and markets. Keep existing building diagnostics and observation ABI
unchanged, preserving historical replay schemas. Expose raw inventories and
production progress with explicit units; do not claim to measure total city
food or include unobserved cargo. Save the new query with run artifacts and
compare it during replay when the source run contains it. Add a bounded recent
cycle history and compact food summaries to the provider-independent context.

**Tech Stack:** C shared library, Python ctypes/Gymnasium, existing JSON command adapter.

**Spec:** The design and constraints in this document.

## Global Constraints

- Preserve normal game rules, action choice, paid ticks and the peaceful mission.
- No thresholds, rankings or forced food/market/culture construction policy.
- Inventories use food units; farm progress is work points, not food produced.
- Market/house inventories and granary inventories are separate containers; cargo and warehouses are not included.
- Keep old `get_buildings` output unchanged and preserve staged user models.
- Work in the existing checkout; no persistent model configuration changes during live trials.

## Review Focus

- Exclude non-food crops and read the correct union member for each building type.
- Native output must fail cleanly on short buffers and never advance time.
- End-of-episode queries and final artifacts must remain available.
- A restored snapshot must recover the detailed food query exactly.
- Recent changes are observations over an elapsed cycle, not causal effects attributed to construction.
- Bound diagnostic samples/history and inspect actual live prompt-token usage.

## Task 1: Native Diagnostics And Artifacts

- [x] Write failing asset-backed query tests and asset-free field/unit tests.
- [x] Add exporter, Python wrapper and shared production-limit accessor.
- [x] Add `final.food_supply.json`, mock artifact checks and conditional strict replay comparison.
- [x] Verify read-only/reset/snapshot/short-buffer/episode-end behavior, review, commit and push.

## Task 2: Planner Feedback

- [ ] Write failing pure-Python tests for food summaries, inventory forecasts and bounded outcome history.
- [ ] Add current food summaries, forecast inventories and four recent observed cycles to model input.
- [ ] Verify existing construction, snapshot, planner and artifact regressions.
- [ ] Run a fixed bounded local-model trial, independently replay it and inspect context size.
- [ ] Record results and limitations, review, commit and push verified source changes only.

## Native Checkpoint Evidence

The query and artifact tests failed before implementation and now pass. Two
asset-free CTests verify physical aggregates and food mapping/units/buffer guards.
The asset-backed food query checks read-only state, snapshot restoration, episode
end and reset. A fresh 12800-tick baseline (suffix `baseline_60850b55`) and strict
food replay pass; historical runs without the new artifact keep their old checks.

Review identified a market slot that can hold either a buyer or labor seeker;
the API exposes raw primary/shared figure IDs instead of mislabeling roles.
Computed road access uses native predicates with NULL result pointers to avoid
mutating the map-point result cache. The raw cached byte is retained separately
because farms/markets do not maintain it as a universal access indicator.
