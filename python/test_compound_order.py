"""Frozen order transforms preserve facts and existing selector contracts."""

import copy
import itertools
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent / "examples"))
import compound_planner_order as order


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.body = {"model": "model", "stream": False, "think": False, "system": "unchanged instructions",
                     "prompt": json.dumps({"decision_id": 2, "state": {"ratings_peace": 0},
                         "native_comparison": {"context_sha256": "source", "alternatives": [
                             {"id": "compound", "forecast": {"treasury": 7499, "food_stocks": 0}, "unknown": None},
                             {"id": "single", "forecast": {"treasury": 7516, "food_stocks": 0}, "unknown": None},
                             {"id": "wait", "forecast": {"treasury": 7566, "food_stocks": 0}, "unknown": None}]}}),
                     "format": {"properties": {"candidate_id": {"type": "string", "enum": list(order.IDS)},
                                                "decision_id": {"type": "integer", "enum": [2]}}},
                     "options": {"num_ctx": 8192, "num_predict": 256, "temperature": .7}}

    def test_all_permutations_preserve_every_fact_and_only_add_seed(self):
        original = copy.deepcopy(self.body)
        facts = json.loads(original["prompt"])["native_comparison"]["alternatives"]
        for ids in itertools.permutations(order.IDS):
            transformed = order.ordered_request(self.body, ids)
            self.assertEqual(transformed["format"]["properties"]["candidate_id"]["enum"], list(ids))
            prompt = json.loads(transformed["prompt"])
            self.assertEqual([row["id"] for row in prompt["native_comparison"]["alternatives"]], list(ids))
            self.assertEqual(sorted(prompt["native_comparison"]["alternatives"], key=lambda r: r["id"]),
                             sorted(facts, key=lambda r: r["id"]))
            self.assertEqual(transformed["options"], {**original["options"], "seed": 20261122})
            restored = copy.deepcopy(transformed)
            restored["options"].pop("seed")
            restored["format"]["properties"]["candidate_id"]["enum"] = list(order.IDS)
            prompt["native_comparison"]["alternatives"] = facts
            restored["prompt"] = json.dumps(prompt)
            self.assertEqual(restored, original)
        self.assertEqual(self.body, original)

    def test_bad_orders_seed_and_tampered_source_domain_reject(self):
        for ids in ((), ("compound", "single"), ("compound", "compound", "wait"),
                    ("compound", "single", "missing"), (True, "single", "wait")):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                order.ordered_request(self.body, ids)
        for seed in (True, -1, 2**31, 1.5):
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                order.ordered_request(self.body, order.IDS, seed=seed)
        bad = copy.deepcopy(self.body)
        bad["format"]["properties"]["candidate_id"]["enum"] = ["compound", "single"]
        with self.assertRaises(ValueError): order.ordered_request(bad, order.IDS)
        bad = copy.deepcopy(self.body)
        prompt = json.loads(bad["prompt"])
        prompt["native_comparison"]["alternatives"][1]["id"] = "compound"
        bad["prompt"] = json.dumps(prompt)
        with self.assertRaises(ValueError): order.ordered_request(bad, order.IDS)

    def test_schedule_is_balanced_and_repeat_requests_are_exact(self):
        schedule = order.schedule()
        self.assertEqual(len(schedule), 14)
        for state in (2, 3):
            conditions = [row for row in schedule if row["decision_id"] == state]
            self.assertEqual(len(conditions), 7)
            permutations = [tuple(row["order"]) for row in conditions if not row["repeat_control"]]
            self.assertEqual(set(permutations), set(itertools.permutations(order.IDS)))
            for position in range(3):
                self.assertEqual(sorted(ids[position] for ids in permutations), sorted(order.IDS * 2))
            control = conditions[-1]
            self.assertTrue(control["repeat_control"])
            self.assertEqual(order.ordered_request(self.body, control["order"]),
                             order.ordered_request(self.body, conditions[0]["order"]))


if __name__ == "__main__":
    unittest.main()
