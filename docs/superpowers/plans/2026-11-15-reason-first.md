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
- [x] Verify local model/digest and native library health without changing server configuration. Run eight model-selected decisions: episode cap 12,800, cadence 800, forecasts 1,600, 8K context, output 256, existing instruct sampling and 170/180-second timeouts. Keep every legal tool; no forced order or policy fallback beyond the existing audited runner behavior.
- [x] Independently replay all recorded actions and strictly compare all six endpoints. Audit every request/error/timeout/token count. Compare actual outcomes to the baseline `planner-local_43337274` at its first eight decisions (6,400 ticks), not its final 16-decision state. Do not promote the profile on rationale claims or tiny samples. Record evidence, limitations and next checkpoint, then commit/push documentation.

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

## Committed Run And Matched Comparison

Implementation `8e87bf6d` was committed/pushed before inference. Run
`planner-local_d86b0c7e` ended at eight decisions / 6,400 ticks, not the episode
cap. Eleven calls produced five accepted housing expansions and six rejected
responses, leading to three explicitly logged wait fallbacks. All attempts
audit the same sampling/context/output settings and `reason_first: true`.
No timeout was reported. Accepted input peak was 7,540 tokens; all rejected
responses reported 8,192. Server logs confirm six input truncations, with raw
prompt sizes 8,560..8,582. Four responses returned inference/output-budget
validation errors and two returned context-headroom errors. The rejected
responses were not accepted as planner decisions. Inference took about 1,277
seconds. Do not call this a clean profile-versus-baseline strategy comparison.

Strict `replay_d12095ac` matches every step and all six final endpoint payloads.
Both original and replay bundles finished without artifact errors or victory.
Replay-derived matched prefix reviews are `planner-prefix-review_c5e9a958`
(baseline, eight of sixteen original decisions) and
`planner-prefix-review_d3810ac3` (this full eight-decision trace). The baseline
also exactly matches its recorded next-context observations at tick 6,400.

| Native Measurement At 6,400 Ticks | Baseline | Reason First Including Fallbacks |
| --- | ---: | ---: |
| Population | 39 | 218 |
| Culture | 0 | 0 |
| Health | 50 | 44 |
| Treasury | 7,542 | 6,977 |
| Residents With Food | 0 | 0 |
| Residents With Fountain Access | 39 | 0 |
| Maximum House Level | 1 | 1 |
| Collected Tax Denarii This Year | 0 | 0 |

Population growth alone is not mission competence: no food or cultural progress
was achieved, health declined, and inference stopped accepting choices once the
legal candidate set grew to 53. There is no simulation population cap here.
The optional profile remains experimental and the default is unchanged.

## Next Bottleneck: Lossless Input Packing

Increasing context previously caused large memory/latency costs; capping city
growth or hiding legal tools would violate this project's intent. An offline
prototype instead represents each candidate's forecast as absolute overrides
of the native wait forecast, preserving every projected value/type and all
candidate IDs/order. No ranking, goal weight or build-order recommendation is
introduced. This is an encoding change, not a new strategy.

One-token `planner-preflight_6bf0bd72` strictly replays the first five committed
blocks to the offending state (4,000 ticks, population 193), verifies the
recorded observations, and roundtrips all 20 scalar forecast fields for all 53
candidates. The prototype loads 5,806 prompt tokens in 8K, reserving room for
256 output tokens plus 128 extra, versus the original first request's 8,569
tokens before server truncation. It completed the one-token probe in about 28
seconds; intentional output-length termination is not an accepted JSON choice.
No new encoding is deployed in the production adapter, and no improvement in
model reasoning or full-mission scalability is established. Implement/test the
optional lossless format before another live strategy run; see the follow-up
forecast-overrides plan.
