"""Water geometry matches native reservoir footprint/range/connectors."""

import unittest
import numpy as np

from julius_gym.water import aqueduct_route, in_reservoir_range, reservoir_ports, reservoir_sites
from julius_gym.diagnostics import water_summary


class WaterPlanningTests(unittest.TestCase):
    def setUp(self):
        self.terrain = np.zeros((22, 22), dtype=np.uint16)
        self.buildings = np.zeros((22, 22), dtype=np.int32)

    def test_midpoint_connectors_and_square_range(self):
        self.assertEqual(set(reservoir_ports((3, 3))), {(4, 2), (6, 4), (4, 6), (2, 4)})
        self.assertTrue(in_reservoir_range((3, 3), (15, 15)))
        self.assertFalse(in_reservoir_range((3, 3), (16, 15)))

    def test_source_footprints_are_clear_and_adjacent_to_water(self):
        self.terrain[5, 10] = 4
        sites = list(reservoir_sites(self.terrain, self.buildings, 22, 22, (10, 10)))
        self.assertTrue(sites)
        for x, y in sites:
            self.assertFalse(self.terrain[y:y + 3, x:x + 3].any())
            self.assertTrue(self.terrain[y - 1:y + 4, x - 1:x + 4].any())

    def test_aqueduct_connects_midpoints_without_crossing_footprints(self):
        path = aqueduct_route(self.terrain, self.buildings, 22, 22, (3, 3), (12, 3))
        self.assertIn(path[0], reservoir_ports((3, 3)))
        self.assertIn(path[-1], reservoir_ports((12, 3)))
        self.assertTrue(all(abs(x - nx) + abs(y - ny) == 1 for (x, y), (nx, ny) in zip(path, path[1:])))
        self.assertFalse(any(3 <= x <= 5 and 3 <= y <= 5 or 12 <= x <= 14 and 3 <= y <= 5 for x, y in path))

    def test_aqueduct_cannot_cross_a_water_barrier(self):
        self.terrain[:, 9] = 4
        with self.assertRaisesRegex(RuntimeError, "aqueduct"):
            aqueduct_route(self.terrain, self.buildings, 22, 22, (3, 3), (12, 3))

    def test_water_feedback_is_bounded_without_dropping_totals(self):
        rows = [{"id": i, "kind": "reservoir", "water_access": i % 2, "workers": 0} for i in range(7)]
        rows.append({"id": 8, "kind": "fountain", "water_access": 1, "workers": 2})
        supply = {"reservoir_radius": 10, "fountain_radius": 4, "buildings": rows,
                  "aqueducts": [{"water": 0}, {"water": 1}]}
        summary = water_summary(supply, [{"population": 40, "fountain": 1, "level": 4}])
        self.assertEqual(summary["supplied_reservoirs"], 3)
        self.assertEqual(summary["reservoirs"], 7)
        self.assertEqual(summary["wet_aqueduct_tiles"], 1)
        self.assertEqual(summary["residents_with_fountain"], 40)
        self.assertEqual(summary["rows_omitted"], 3)


if __name__ == "__main__":
    unittest.main()
