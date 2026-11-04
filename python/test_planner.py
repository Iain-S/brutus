"""Planner boundary tests; no licensed game data or local model needed."""

import sys
import unittest
from julius_gym.planner import Candidate, command_choice, validate_choice, execute


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.context = {"decision_id": 7}
        self.candidates = {"wait": Candidate("wait", [(0, 0, 0)], "state", {})}
        self.choice = {"decision_id": 7, "candidate_id": "wait", "reason": "Observe effects"}

    def test_valid_choice(self):
        self.assertIs(validate_choice(self.choice, self.context, self.candidates), self.candidates["wait"])

    def test_rejects_stale_unknown_and_extra_fields(self):
        for change in ({"decision_id": 6}, {"candidate_id": "invented"},
                       {"python": "arbitrary code"}, {"decision_id": True}, {"reason": 42}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_choice({**self.choice, **change}, self.context, self.candidates)

    def test_local_command_round_trip(self):
        command = [sys.executable, "-c", "import json,sys; c=json.load(sys.stdin); print(json.dumps(dict(decision_id=c['decision_id'],candidate_id='wait',reason='test adapter')))" ]
        result = command_choice(command, self.context)
        self.assertIs(validate_choice(result, self.context, self.candidates), self.candidates["wait"])

    def test_failed_command_is_rejected(self):
        with self.assertRaises(ValueError):
            command_choice([sys.executable, "-c", "raise SystemExit(1)"], self.context)

    def test_non_json_command_is_rejected(self):
        with self.assertRaises(ValueError):
            command_choice([sys.executable, "-c", "print('not JSON')"], self.context)


if __name__ == "__main__":
    unittest.main()
