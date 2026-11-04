"""Geometry regressions for placement rules that success messages cannot catch."""

import unittest
import numpy as np

from julius_gym.baseline import ROAD, building_plan, connected_roads, exclude_hazard
from julius_gym.env import ActionType


class PlacementTests(unittest.TestCase):
    def test_hazard_mask_preserves_engine_map_and_access(self):
        terrain = np.zeros((12, 12), dtype=np.uint16)
        terrain[6, 6] = ROAD
        terrain[7, 6] = 4
        masked = exclude_hazard(terrain, {"severity": 3, "x": 6, "y": 6}, 2)
        self.assertEqual(terrain[5, 5], 0)
        self.assertEqual(masked[5, 5], 2)
        self.assertEqual(masked[6, 6], ROAD)
        self.assertEqual(masked[7, 6], 4)
        self.assertEqual(masked[0, 0], 0)

    def setUp(self):
        self.terrain = np.zeros((30, 30), dtype=np.uint16)
        self.buildings = np.zeros_like(self.terrain)
        self.terrain[15, :21] = ROAD
        self.entry = (0, 15)

    def test_granary_entrance_meets_center_of_edge(self):
        actions = building_plan(self.terrain, self.buildings, 30, 30, self.entry,
                                ActionType.BUILD_GRANARY, 3)
        kind, x, y = actions[-1]
        for action, rx, ry in actions[:-1]:
            if action == ActionType.BUILD_ROAD:
                self.terrain[ry, rx] = ROAD
        self.assertEqual(kind, ActionType.BUILD_GRANARY)
        entrances = ((x + 1, y - 1), (x + 3, y + 1), (x + 1, y + 3), (x - 1, y + 1))
        self.assertTrue(any(self.terrain[ey, ex] & ROAD for ex, ey in entrances))

    def test_local_service_stays_near_anchor(self):
        actions = building_plan(self.terrain, self.buildings, 30, 30, self.entry,
                                ActionType.BUILD_PREFECTURE, 1, anchor=(19, 12))
        _, x, y = actions[-1]
        self.assertLessEqual(abs(x - 19) + abs(y - 12), 4)

    def test_disconnected_road_is_not_used_as_root(self):
        self.terrain[4, 4:8] = ROAD
        roads = connected_roads(self.terrain, 30, 30, self.entry)
        self.assertNotIn((4, 4), roads)
        self.assertIn((20, 15), roads)


if __name__ == "__main__":
    unittest.main()
