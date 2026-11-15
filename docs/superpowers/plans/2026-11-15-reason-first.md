# Optional Reason-First Planner Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans with TDD and one final source review. Preserve user-staged models.

**Goal:** Evaluate an optional generic comparison-before-choice profile against actual native game outcomes, without prescribing a build order.

**Spec:** The approved next checkpoint in `2026-11-12-planner-context-guard.md`, including the small frozen-state probe and its inaccurate rationales.

**Architecture:** Add `reason_first=False` to `request_body()` and a matching
`--reason-first` CLI flag. Only the optional profile changes schema property and
required-key order to reason/decision_id/candidate_id and requests a brief
comparison before choice. Keep the three-field protocol, candidate enum, all
native tools, sampling/context/output budgets and default request unchanged.
Audit the profile explicitly on stderr, including rejected responses. Reasons
remain untrusted model text, never measurements or verified predictions.

**Tech Stack:** Existing Python standard-library Ollama adapter, unittest,
canonical Gym library/environment and durable campaign run artifacts.

## Tasks

- [x] Write and observe failing tests for opt-in schema ordering, preserved facts/candidates/options/defaults, both CLI modes and profile audit metadata. Implement the minimal adapter change; run focused suites, source review, document usage and commit/push source only.
- [ ] Verify local model/digest and native library health without changing server configuration. Run eight model-selected decisions: episode cap 12,800, cadence 800, forecasts 1,600, 8K context, output 256, existing instruct sampling and 170/180-second timeouts. Keep every legal tool; no forced order or policy fallback beyond the existing audited runner behavior.
- [ ] Independently replay all recorded actions and strictly compare all six endpoints. Audit every request/error/timeout/token count. Compare actual outcomes to the baseline `planner-local_43337274` at its first eight decisions (6,400 ticks), not its final 16-decision state. Do not promote the profile on rationale claims or tiny samples. Record evidence, limitations and next checkpoint, then commit/push documentation.

## Rulings

- Continue in the existing dedicated feature branch/workspace, as authorized throughout this task; do not create/switch worktrees or disturb staged artifacts and canonical local paths.
- The design is already selected and the user requested continuation. No new model installation, external provider, native gameplay change or repeated design approval is needed.
- No trained weights, original assets, local configuration, game logs or run bundles enter commits. Use explicit source paths and `git commit --only`.
- A timeout, exhausted context/output or replay mismatch is evidence to diagnose, not a reason to weaken validation. No mission-win claim is possible from this short trial alone.

## Adapter Verification

Observed RED for missing request keyword, CLI flag and audit field, then GREEN:
51 focused planner tests and seven replay tests. A direct comparison against
the pre-change builder confirms byte-identical default rows/objects requests;
the optional request matches the prior full-option frozen probe byte-for-byte.
Fresh source review found no blockers and independently checked eight default
request cases. The implicit/explicit-default unit test is not itself a frozen
baseline; direct differential verification supplements it for this checkpoint.

Five available native CTests, nested/reset-failure snapshot boundaries and
Python dependency checks pass; no native source changed. The installed instruct
model digest matches the pinned prior trial. No server settings or model
installations changed. User-staged model artifacts remain excluded.
