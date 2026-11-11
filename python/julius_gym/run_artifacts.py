"""Unique, durable review artifacts for campaign runner invocations."""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4

DEFAULT_RUNS = Path(__file__).resolve().parents[2] / "runs"


class RunArtifacts:
    def __init__(self, mode, root=DEFAULT_RUNS, log=None, configuration=None):
        now = datetime.now(timezone.utc)
        self.directory = (Path(root).resolve() / "tarraco" / now.strftime("%Y-%m-%d") /
                          (now.strftime("%Y%m%dT%H%M%S.%fZ") + f"_{mode}_{uuid4().hex[:8]}"))
        self.directory.mkdir(parents=True, exist_ok=False)
        self.log = Path(log).resolve() if log else self.directory / "actions.jsonl"
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.started = time.monotonic()
        self.ready = False
        self.metadata = {"schema_version": 1, "mode": mode, "started_utc": now.isoformat(),
                         "configuration": configuration or {}, "status": "initializing",
                         "actions": str(self.log), "render_status": "manual_capture_pending"}
        try:
            self.metadata["git_commit"] = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[2],
                capture_output=True, text=True, timeout=5, check=True).stdout.strip()
            self.metadata["git_dirty"] = bool(subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=no"],
                cwd=Path(__file__).resolve().parents[2], capture_output=True, text=True,
                timeout=5, check=True).stdout.strip())
        except (OSError, subprocess.SubprocessError):
            self.metadata["git_commit"] = None
        self._write()

    def _write(self):
        (self.directory / "run.json").write_text(json.dumps(self.metadata, indent=2, default=str), encoding="utf-8")

    def finish(self, env, summary=None, error=None):
        """Called before env.close(), also on exceptions and KeyboardInterrupt."""
        failures = []
        self.metadata.update({"wall_seconds": time.monotonic() - self.started,
                              "ended_utc": datetime.now(timezone.utc).isoformat(),
                              "status": "error" if error else "finished", "summary": summary})
        if error:
            self.metadata["error"] = f"{type(error).__name__}: {error}"
        if self.ready:
            for name, write in (
                ("final.sav", lambda: env.export_save(self.directory / "final.sav")),
                ("final.buildings.json", lambda: (self.directory / "final.buildings.json").write_text(
                    json.dumps(env.get_buildings(), indent=2), encoding="utf-8")),
                ("final.food_supply.json", lambda: (self.directory / "final.food_supply.json").write_text(
                    json.dumps(env.get_food_supply(), indent=2), encoding="utf-8")),
                ("final.imperial.json", lambda: (self.directory / "final.imperial.json").write_text(
                    json.dumps(env.get_imperial_state(), indent=2), encoding="utf-8")),
            ):
                try:
                    write()
                except Exception as failure:
                    failures.append(f"{name}: {failure}")
            try:
                self.metadata["victory_state"] = env.get_victory_state()
            except Exception as failure:
                failures.append(f"victory_state: {failure}")
        else:
            self.metadata["save_status"] = "not_available_reset_did_not_complete"
        self.metadata["artifact_errors"] = failures
        (self.directory / "REVIEW.md").write_text(
            "# Manual Review\n\nOpen final.sav in graphical Julius using the original game data.\n"
            "Pause immediately, then press Ctrl+F12 for a full-city screenshot using real assets.\n"
            "Move/rename that PNG to final.png in this folder. No PNG has been rendered automatically.\n"
            "Keep final.sav for interactive inspection. See run.json for outcome and artifact errors.\n",
            encoding="utf-8")
        self._write()
        print(f"Run artifacts: {self.directory}")
        if failures:
            message = "Final artifact export failed: " + "; ".join(failures)
            if error is None:
                raise RuntimeError(message)
            print(message, file=sys.stderr)
