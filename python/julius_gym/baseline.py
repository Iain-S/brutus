"""Deterministic starter settlement: an entry-connected street with water/services."""

from collections import deque

from .env import ActionType

ROAD = 0x40
NOT_CLEAR = 0xD77F


def exclude_hazard(terrain, earthquake, radius):
    """Mask new land construction near the quake origin; leave engine state alone.

    This is a conservative siting heuristic, not a prediction of the quake path.
    Existing roads remain usable, so access routes still need runtime monitoring.
    """
    result = terrain.copy()
    if radius and earthquake.get("severity"):
        cx, cy = earthquake["x"], earthquake["y"]
        for y in range(max(0, cy - radius), min(result.shape[0], cy + radius + 1)):
            for x in range(max(0, cx - radius), min(result.shape[1], cx + radius + 1)):
                if not result[y, x] & (ROAD | 4):
                    result[y, x] |= 2
    return result


def local_roads(roads, anchor):
    if anchor is None or not roads:
        return roads
    distance = lambda p: abs(p[0] - anchor[0]) + abs(p[1] - anchor[1])
    nearest = min(map(distance, roads))
    return {point for point in roads if distance(point) <= nearest + 2}


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


def starter_plan(terrain, buildings, width, height, entry, length=6, anchor=None):
    """Find a clear three-tile-wide strip reachable from the entry road.

    A single street serves houses, a well and safety services on both sides.
    BFS chooses a short clear connection to existing entry roads.
    """
    roads = connected_roads(terrain, width, height, entry)
    if not roads:
        raise RuntimeError("No road connected to the entry; refusing an isolated settlement")
    roots = local_roads(roads, anchor)
    parents = {point: None for point in roots}
    pending = deque(sorted(roots, key=lambda p: (abs(p[0] - anchor[0]) + abs(p[1] - anchor[1]), p)
                           if anchor else (0, p)))

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
                        5: ActionType.BUILD_ENGINEERS_POST, 6: ActionType.BUILD_WELL}
            actions += [(kind, *tile(i, 1)) for i, kind in services.items() if i <= length]
            actions += [(ActionType.BUILD_HOUSING, *tile(i, side))
                        for i in range(1, length + 1) for side in (-1, 1)
                        if side == -1 or i not in services]
            return actions
        for point in neighbors(origin, width, height):
            if point not in parents and (clear(point) or point in roads):
                parents[point] = origin
                pending.append(point)
    raise RuntimeError("No connected clear strip found for starter settlement")


def building_plan(terrain, buildings, width, height, entry, kind, size, meadow=False, anchor=None):
    """Place a footprint beside an entry-connected road, adding a short access road."""
    roads = connected_roads(terrain, width, height, entry)
    roots = local_roads(roads, anchor)
    parents = {point: None for point in roots}
    pending = deque(sorted(roots, key=lambda p: (abs(p[0] - anchor[0]) + abs(p[1] - anchor[1]), p)
                           if anchor else (0, p)))

    def clear(x, y):
        return (0 < x < width - 1 and 0 < y < height - 1
                and not terrain[y, x] & (NOT_CLEAR & ~0x11) and not buildings[y, x])

    while pending:
        road = pending.popleft()
        rx, ry = road
        path = []
        cursor = road
        while cursor is not None and cursor not in roads:
            path.append(cursor)
            cursor = parents[cursor]
        sites = ((rx + 1, ry), (rx - size, ry), (rx, ry + 1), (rx, ry - size))
        if kind == ActionType.BUILD_GRANARY:
            # Granaries accept access at the middle of an edge, not a corner.
            sites = ((rx + 1, ry - 1), (rx - size, ry - 1),
                     (rx - 1, ry + 1), (rx - 1, ry - size))
        for x, y in sites:
            if meadow and any(terrain[ny, nx] & 4 for nx, ny in neighbors(road, width, height)):
                continue  # Keep the narrow bridge landing open for the farm district.
            footprint = [(x + dx, y + dy) for dx in range(size) for dy in range(size)]
            if not all(clear(tx, ty) for tx, ty in footprint):
                continue
            # Match the engine: farms need meadow within one tile of the footprint.
            if meadow and not any(terrain[ty, tx] & 0x800
                                  for tx in range(max(0, x - 1), min(width, x + size + 1))
                                  for ty in range(max(0, y - 1), min(height, y + size + 1))):
                continue
            if any(point in footprint for point in path):
                continue
            clearing = sorted({point for point in footprint + path
                               if terrain[point[1], point[0]] & 0x11})
            return ([(ActionType.CLEAR_LAND, *point) for point in clearing]
                    + [(ActionType.BUILD_ROAD, *point) for point in reversed(path)]
                    + [(kind, x, y)])
        for point in neighbors(road, width, height):
            if point not in parents and (clear(*point) or point in roads):
                parents[point] = road
                pending.append(point)
    raise RuntimeError(f"No connected footprint for action {kind}")


def bridge_plan(env, entry, earthquake=None, radius=0):
    """Find an engine-valid crossing from reachable land toward meadow."""
    terrain, buildings, width, height = env.get_map_data()
    terrain = exclude_hazard(terrain, earthquake or {}, radius)
    roads = connected_roads(terrain, width, height, entry)
    parents = {point: None for point in roads}
    pending = deque(sorted(roads))
    while pending:
        point = pending.popleft()
        for neighbor in neighbors(point, width, height):
            x, y = neighbor
            if neighbor in parents or not (0 < x < width - 1 and 0 < y < height - 1):
                continue
            if terrain[y, x] & 4:
                length, direction = env.bridge_span(x, y)
                if not length:
                    continue
                dx, dy = {0: (0, -1), 2: (1, 0), 4: (0, 1), 6: (-1, 0)}[direction]
                if (x - dx, y - dy) != point:
                    continue
                landing = x + length * dx, y + length * dy
                lx, ly = landing
                if not (0 < lx < width - 1 and 0 < ly < height - 1):
                    continue
                if terrain[ly, lx] & NOT_CLEAR or buildings[ly, lx]:
                    continue
                path = []
                cursor = point
                while cursor is not None and cursor not in roads:
                    path.append(cursor)
                    cursor = parents[cursor]
                # Prefer a crossing that makes a farm site reachable in the map model.
                preview = terrain.copy()
                for px, py in path + [landing]:
                    preview[py, px] = ROAD
                for i in range(length):
                    preview[y + i * dy, x + i * dx] |= ROAD
                try:
                    building_plan(preview, buildings, width, height, entry,
                                  ActionType.BUILD_WHEAT_FARM, 3, True)
                except RuntimeError:
                    continue
                clearing = [p for p in path if terrain[p[1], p[0]] & 0x11]
                return ([(ActionType.CLEAR_LAND, *p) for p in clearing]
                        + [(ActionType.BUILD_ROAD, *p) for p in reversed(path)]
                        + [(ActionType.BUILD_LOW_BRIDGE, x, y),
                           (ActionType.BUILD_ROAD, *landing)])
            if not terrain[y, x] & (NOT_CLEAR & ~0x11) and not buildings[y, x]:
                parents[neighbor] = point
                pending.append(neighbor)
    raise RuntimeError("No valid bridge to accessible farmland found")
