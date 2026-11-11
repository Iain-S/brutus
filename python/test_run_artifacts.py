"""Artifact naming, durable saves, and failure recording without game data."""

import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from julius_gym.run_artifacts import DEFAULT_RUNS, RunArtifacts


class ArtifactTests(unittest.TestCase):
    def test_unique_runs_and_error_export(self):
        DEFAULT_RUNS.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=DEFAULT_RUNS) as root:
            first = RunArtifacts("baseline", root)
            second = RunArtifacts("baseline", root)
            self.assertNotEqual(first.directory, second.directory)
            env = SimpleNamespace(export_save=lambda p: p.write_bytes(b"test save"),
                                  get_buildings=lambda: [], get_victory_state=lambda: 0,
                                  get_food_supply=lambda: {"schema_version": 1, "buildings": []})
            env.get_imperial_state = lambda: {"schema_version": 1, "personal_savings": 100, "favor": 53}
            first.ready = True
            first.finish(env, error=RuntimeError("test failure"))
            self.assertTrue((first.directory / "final.sav").exists())
            self.assertEqual(json.loads((first.directory / "final.imperial.json").read_text()), env.get_imperial_state())
            self.assertEqual(json.loads((first.directory / "final.food_supply.json").read_text()),
                             env.get_food_supply())
            metadata = json.loads((first.directory / "run.json").read_text())
            self.assertEqual(metadata["status"], "error")
            self.assertIn("test failure", metadata["error"])
            self.assertEqual(metadata["render_status"], "manual_capture_pending")
            self.assertFalse((first.directory / "final.png").exists())

    def test_no_save_when_reset_failed(self):
        DEFAULT_RUNS.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=DEFAULT_RUNS) as root:
            run = RunArtifacts("baseline", root)
            run.finish(None, error=ValueError("reset failed"))
            self.assertFalse((run.directory / "final.sav").exists())
            metadata = json.loads((run.directory / "run.json").read_text())
            self.assertEqual(metadata["save_status"], "not_available_reset_did_not_complete")


if __name__ == "__main__":
    unittest.main()
