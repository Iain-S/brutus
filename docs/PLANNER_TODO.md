# Campaign Planner Remaining Work

Updated: 2026-11-22. Compound-model source: `03089798`; preview foundation: `3ce633ac`.
See [results and evidence](PLANNER_RESULTS.md) before interpreting progress.

## Completed Checkpoint: Native Compound Previews

The native two-step interface and engineering controls are implemented. The
separate compound experiment is now evaluated below; the standard planner is unchanged.

- [x] Define a bounded short-plan interface, initially two steps, and how
  future actions are identified without trusting stale candidate objects.
- [x] Regenerate and validate legal candidates in each simulated successor
  state. A legal first action must not authorize an unchecked second action.
- [x] Preview compound plans inside an outer native snapshot; restore the
  base state on success, invalid future action, termination, or exception.
- [x] Charge actual action and observation ticks against the real budget.
  Include an equal-time wait control; do not compare unequal simulated time.
- [x] Record per-step legality, messages, rewards, ticks, costs, staffing,
  food and ratings, plus final native diagnostic payloads.
- [x] Add focused unit tests before implementation, covering invalid and
  stale successors, budget exhaustion, terminal states, and restoration.
- [x] Recheck native health, then prove compound rollback and independent
  replay against all six diagnostic endpoints before trusting forecasts.
- [x] Obtain source review and commit verified source changes separately
  from generated artifacts and the user's staged model files.

## Completed Checkpoint: Bounded Model Feasibility Evaluation

The separate audited command and sequential proposal protocol are documented in
`python/examples/PLANNER.md`. Four decisions/twelve model calls deliver 6400 ticks
and pass independent protocol audit and native replay. Final population is 49
with fountain coverage 49; food delivery/culture/prosperity remain zero. The
model declines one second water build, but better campaign play is not established.
A legal first step still never authorizes an unchecked second action.

- [x] Run a small audited experiment with model-proposed short plans only
  after native controls pass. Do not supply a hand-picked winning sequence.
- [x] Compare explicit native goal and state outcomes at equal charged time,
  without introducing human-weighted scores or changing simulation rules.
- [x] Keep proposal validity, forecast reliability, action execution, and
  strategic improvement as separate acceptance gates.
- [x] Record failures as failures; do not weaken validation or replay checks
  to promote a run. Distinguish predicted outcomes from delivered outcomes.
- [x] Decide from evidence whether planning depth helps or whether model
  capability, lookup anchoring, or tool coverage needs separate investigation.
  A larger model is an option to evaluate, not an established requirement.

## Next Checkpoint: Planning Quality Diagnosis

- [ ] Use the frozen audited comparisons to examine selection of additional
  construction with no improvement in named native goal/service endpoints and
  lower treasury. Do not infer verified reasoning from ID-only answers.
- [ ] Choose a separately controlled diagnostic for root selection/search
  breadth, model capability or horizon. The feasibility run isolates none of
  these. Include presentation/order controls if comparing frozen selections.
- [ ] Account for food/staffing and annual-rating timescales before choosing
  a longer native evaluation. Keep all legal choices available and avoid a
  prescribed winning sequence or human-weighted score.
- [ ] Require demonstrable delivered multi-goal progress before promoting the
  compound policy or extending it unchanged toward a whole-campaign attempt.

## Campaign Completion And Optimization

- [ ] Demonstrate sustained food delivery, useful service coverage, housing
  evolution, staffing, and solvent finances under native rules.
- [ ] Demonstrate all native Tarraco win conditions over the required annual
  updates; short population-growth prefixes are not sufficient.
- [ ] Once reliable wins exist, compare native time-to-victory across repeated
  runs with documented seeds/settings, costs, failures, and inference time.
- [ ] Extend to additional peaceful missions only when the first mission's
  validity and performance are established. Combat remains out of scope.

## Artifacts And Review

- [ ] Continue creating real native saves, six diagnostics and review notes
  for every actual campaign run, using the established directory convention.
- [ ] Render at least one final native save through graphical Julius with
  the real game assets, and retain `final.png` for manual review.
- [ ] Establish a repeatable real-asset screenshot workflow if practical;
  keep manual/pending status explicit until it actually works.
- [ ] Update this checklist and the results summary at each checkpoint,
  linking new evidence and preserving historical failed experiments.

## Constraints To Preserve

No population caps, modified victory rules, human-prescribed build order,
combat, fabricated evidence, or unvalidated future actions. Do not commit
original game assets, generated runs, environments, or trained models.
Preserve unrelated staged work. The previous DLL security block was resolved
by the user; it is not a current blocker and no security-policy changes are
part of this work.
