# Campaign Run Records

The baseline and planner runners now create unique folders under the checkout's
ignored `runs/` directory, regardless of the directory they are launched from.
Rebuild `julius_gym` to enable durable save export.

```text
runs/
  tarraco/
    2026-11-07/
      20261107T135658.202869Z_planner-smoke_2761a253/
        actions.jsonl
        run.json
        final.sav
        final.buildings.json
        final.food_supply.json
        final.imperial.json
        final.water_supply.json
        REVIEW.md
        final.png                 (add manually after Julius capture)
```

Date and timestamp use UTC. Mode is `baseline`, `planner-smoke`,
`planner-local`, `imperial-capability`/`water-capability` (native integration checks), or `replay`. The random suffix avoids collisions, including simultaneous
runs. Filenames inside a run stay fixed so they are easy to compare.

- `actions.jsonl`: action/decision records.
- `run.json`: configuration, mission identity, source commit and dirty flag,
  outcome/summary, elapsed wall time, errors, and manual-render status.
- `final.sav`: persistent standard game save for interactive Julius review.
- `final.buildings.json`: engine building/service diagnostics at the end.
- `final.food_supply.json`: separate farm progress and granary/market inventories;
  excludes cargo, warehouses and household inventory (the latter is in building diagnostics).
- `final.imperial.json`: personal savings/salary, favor, gift timing/penalty and
  fresh native gift quotes, separate from city treasury.
- `final.water_supply.json`: full cached native water-structure diagnostics and
  aqueduct wet/dry tiles, without recalculating supply.
- `REVIEW.md`: screenshot capture instructions for that folder.
- `final.png`: reserved name for the real-assets Julius screenshot; not created
  or imitated by the headless runner.

Saves are exported before environment cleanup on ordinary exits, simulation
timeouts, decision-budget stops and Python exceptions/interrupts after reset.
The end state can be a failed or partial run; consult `run.json`. If reset never
completed, the manifest explicitly marks the save unavailable. Export failures
are recorded and reported. Process kills, native crashes and power loss cannot
guarantee a final save; the initial manifest may remain `initializing`.

Use `--runs-dir <ABSOLUTE_OUTPUT_ROOT>` to put the same hierarchy elsewhere.
The legacy `--log <PATH>` override remains for existing tests/scripts; it writes
the action log at that exact location, while the final save and manifest still
go into a unique run folder. Without this override, the run folder contains all
review artifacts. Existing legacy logs and runs are not renamed or migrated.
The baseline also retains its legacy log-adjacent `.buildings.json` file.

## Review With Real Assets

Open `final.sav` in graphical Julius with the original Caesar III assets. If the
load dialog cannot browse to the run directory, copy the save to the location
listed by that Julius installation's load dialog using a distinctive filename.
Retain the original run-folder save as the source artifact.

Pause immediately after loading. Press **Ctrl+F12** to capture the full city,
then move/rename Julius's timestamped PNG to `final.png` in the run folder.
The image uses Julius's renderer and loaded assets rather than the Python debug
map. Current capture is manual and can advance time before pausing; automatic
load-paused rendering is a later improvement for exact frame correspondence.
Keep the save for inspecting houses, service overlays and advisors.

These conventions currently cover `run_baseline.py` and `run_planner.py`.
Legacy RL training examples retain their own model/checkpoint layout.

## Independent Replay

```shell
python examples/replay_run.py <ABSOLUTE_RUN_FOLDER> --data-dir <ABSOLUTE_DATA_DIRECTORY> --lib-path <ABSOLUTE_LIBRARY_PATH>
```

For finished campaign runs with manifests and logs, this starts the mission
again and executes only the recorded actions. It makes no model calls and no
snapshot previews. It checks each result message/reward and the final building
diagnostics, population and authoritative victory state. A new `replay` folder
contains its own final save and manifest, including any divergence error.
Use matching game data, library and game settings. A replay failure is evidence
to investigate, not something the script silently repairs. This verifies action
execution determinism, not repeatability or quality of the model's decisions.

When the source run includes `final.food_supply.json`, replay also compares that
entire versioned payload strictly and reports `food_supply_verified: true`.
Older runs without it retain their existing checks and report this extra check
as false; no historical food observations are invented or silently migrated.

When `final.imperial.json` is present, replay strictly compares its whole
diagnostic payload and reports `imperial_state_verified: true`. Older bundles
without it retain their existing checks and report this extra check as false.
The query does not include every GUI-only cached gift field; normal save files
retain those native fields for interactive review.

When `final.water_supply.json` is present, replay strictly compares all structure
and aqueduct diagnostics and reports `water_supply_verified: true`. Older bundles
without it retain existing checks and report this extra check as false. New
output bundles do not rewrite historical source diagnostics.
