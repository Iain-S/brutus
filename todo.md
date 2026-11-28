# Training Gym roadmap

The immediate goal is to make the Julius Gym environment suitable for two
related use cases:

1. find fast, reliable winning plans for a fixed Caesar III scenario;
2. later train policies that generalise across scenarios.

The current environment is a useful integration prototype, but it is not yet
a sound training benchmark. Build actions use a fixed map coordinate, the
observation has no spatial state, invalid actions are sampled rather than
masked, and the current population-year wrapper changes the task away from
winning the scenario.

## Priority 0: reproducible benchmark and state restore

Before changing algorithms, make a fixed scenario reproducible and support
reliable reset plus snapshot/restore. This is required for trustworthy policy
evaluation and will enable state-archive planning (for example Go-Explore) for
fast scenario solutions.

Acceptance criteria:

- A configured scenario can be reset repeatedly in one process with no crash,
  state leakage, or result drift.
- A fixed action sequence produces the same observations, rewards, termination
  flags, and relevant map state across repeated runs from the same reset.
- A snapshot taken after an action prefix can be restored; the same suffix then
  produces the same result as the uninterrupted episode.
- A command-line evaluation harness records scenario ID, library revision,
  seed/configuration, win rate, ticks-to-victory, and failure reason.

Implementation outline:

1. Audit the existing game save/load path and identify an in-memory-safe state
   boundary. Prefer a supported scenario/save serialisation path over copying
   global C memory.
2. Extend the C Gym API with explicit reset configuration and opaque snapshot
   handles (create, restore, destroy), keeping ownership clear across the C and
   Python boundary.
3. In Python, expose reset seed/configuration and a small snapshot context or
   explicit handle API. Do not make `reset()` silently reuse a partially played
   game.
4. Add C/Python regression tests for repeatability and branching from a
   snapshot. Run them against a supplied test scenario/data fixture where
   licensing permits; otherwise make the required paths environment variables
   and skip clearly when absent.
5. Add a fixed-scenario evaluator before treating model artifacts as results.

## Priority 1: decision interface

Status: the first road/housing candidate-site curriculum is implemented. It
uses a small fixed-scenario action space and legal-action masking; it is a
validated learning milestone, not yet the general Caesar III interface.

Replace fixed-coordinate actions with a manageable spatial decision interface.
Start with a small, scenario-derived candidate-site set and macro-actions:

- place a housing block or service at a candidate site;
- connect selected sites with roads;
- place farm/industry only on eligible terrain;
- clear a candidate area;
- advance multiple game ticks.

Expose a legal-action mask and structured failure reason. Begin with
MaskablePPO as a baseline after the mask is available. Keep the same action
wrapper and mapping for training and evaluation.

## Priority 2: observations and objective

Add compact spatial layers (terrain, buildability, roads, buildings) and
candidate-site features. Retain useful aggregate statistics, but do not ask a
policy to infer map layout from aggregates.

Make scenario victory the primary objective: a large terminal win reward plus
a small per-tick cost. Progress shaping should reflect scenario-goal progress
and be evaluated against the unshaped objective. Preserve Gymnasium semantics:
an artificial rollout/time boundary is `truncated`, while a true win/loss is
`terminated`.

## Priority 3: search, imitation, then general RL

For one scenario, use snapshot-backed state-archive search to discover winning
plans. Score states by progress and elapsed ticks, restore promising states,
and explore short macro-action branches. Turn successful traces into
behaviour-cloning data, then fine-tune a masked policy for robustness.

Once the benchmark and interface are stable, compare MaskablePPO against a
world-model approach for long-horizon training. Do not interpret improvements
in shaped reward as scenario-playing progress without the fixed evaluator.
