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
        REVIEW.md
        final.png                 (add manually after Julius capture)
```

Date and timestamp use UTC. Mode is `baseline`, `planner-smoke`, or
`planner-local`. The random suffix avoids collisions, including simultaneous
runs. Filenames inside a run stay fixed so they are easy to compare.

- `actions.jsonl`: action/decision records.
- `run.json`: configuration, mission identity, source commit and dirty flag,
  outcome/summary, elapsed wall time, errors, and manual-render status.
- `final.sav`: persistent standard game save for interactive Julius review.
- `final.buildings.json`: engine building/service diagnostics at the end.
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
