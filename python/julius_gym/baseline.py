"""Deterministic starter settlement: an entry-connected street with water/services."""

from collections import deque

from .env import ActionType

ROAD = 0x40
NOT_CLEAR = 0xD77F


def neighbors(point, width, height):
    x, y = point
    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
        if 0 <= nx < width and 0 <= ny < height:
            yield nx, ny


def connected_roads(terrain, width, height, entry):
    """Flood only the road component touching the mission's entry tile."""
    seeds = [tuple(entry), *neighbors(entry, width, height)]
    roads = {p for p in seeds if terrain[p[1], p[0]] & ROAD}
    pending = deque(sorted(roads))
    while pending:
        for point in neighbors(pending.popleft(), width, height):
            x, y = point
            if point not in roads and terrain[y, x] & ROAD:
                roads.add(point)
                pending.append(point)
    return roads


def starter_plan(terrain, buildings, width, height, entry, length=6):
    """Find a clear three-tile-wide strip reachable from the entry road.

    A single street serves houses, a well and safety services on both sides.
    BFS chooses a short clear connection to existing entry roads.
    """
    roads = connected_roads(terrain, width, height, entry)
    if not roads:
        raise RuntimeError("No road connected to the entry; refusing an isolated settlement")
    parents = {point: None for point in roads}
    pending = deque(sorted(roads))

    def clear(point):
        x, y = point
        return (0 < x < width - 1 and 0 < y < height - 1
                and not terrain[y, x] & NOT_CLEAR and not buildings[y, x])

    while pending:
        origin = pending.popleft()
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            px, py = -dy, dx
            def tile(i, side):
                return origin[0] + i * dx + side * px, origin[1] + i * dy + side * py
            if not all(clear(tile(i, side)) for i in range(1, length + 1)
                       for side in range(-1, 2)):
                continue
            path = []
            cursor = origin
            while cursor is not None and cursor not in roads:
                path.append(cursor)
                cursor = parents[cursor]
            actions = [(ActionType.BUILD_ROAD, *point) for point in reversed(path)]
            actions += [(ActionType.BUILD_ROAD, *tile(i, 0)) for i in range(1, length + 1)]
            # Reserve road-front positions for wells and staffed safety services.
            services = {2: ActionType.BUILD_WELL, 3: ActionType.BUILD_PREFECTURE,
                        5: ActionType.BUILD_ENGINEERS_POST}
            actions += [(kind, *tile(i, 1)) for i, kind in services.items() if i <= length]
            actions += [(ActionType.BUILD_HOUSING, *tile(i, side))
                        for i in range(1, length + 1) for side in (-1, 1)
                        if side == -1 or i not in services]
            return actions
        for point in neighbors(origin, width, height):
            if point not in parents and clear(point):
                parents[point] = origin
                pending.append(point)
    raise RuntimeError("No connected clear strip found for starter settlement")
