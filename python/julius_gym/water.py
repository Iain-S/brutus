"""Bounded, native-validated water construction; no simulation rule changes."""

from collections import deque

from .baseline import NOT_CLEAR, building_plan, exclude_hazard, neighbors
from .env import ActionType as A

AQUEDUCT = 0x100


def reservoir_ports(site):
    x, y = site
    return ((x + 1, y - 1), (x + 3, y + 1), (x + 1, y + 3), (x - 1, y + 1))


def in_reservoir_range(site, point):
    x, y = site
    return x - 10 <= point[0] <= x + 12 and y - 10 <= point[1] <= y + 12


def reservoir_sites(terrain, buildings, width, height, anchor, near_water=True):
    sites = []
    for y in range(1, height - 3):
        for x in range(1, width - 3):
            if any(buildings[ty, tx] or terrain[ty, tx] & (NOT_CLEAR & ~0x11)
                   for ty in range(y, y + 3) for tx in range(x, x + 3)):
                continue
            if near_water and not any(terrain[ty, tx] & 4
                    for ty in range(y - 1, y + 4) for tx in range(x - 1, x + 4)):
                continue
            sites.append((x, y))
    return sorted(sites, key=lambda p: (abs(p[0] + 1 - anchor[0]) + abs(p[1] + 1 - anchor[1]), p))


def aqueduct_route(terrain, buildings, width, height, source, target):
    reserved = {(x + dx, y + dy) for x, y in (source, target) for dx in range(3) for dy in range(3)}

    def clear(point):
        x, y = point
        return (0 < x < width - 1 and 0 < y < height - 1 and point not in reserved
                and not buildings[y, x] and not terrain[y, x] & (NOT_CLEAR & ~(0x11 | AQUEDUCT)))

    starts = [p for p in reservoir_ports(source) if clear(p)]
    goals = {p for p in reservoir_ports(target) if clear(p)}
    parents = {p: None for p in starts}
    pending = deque(starts)
    while pending:
        point = pending.popleft()
        if point in goals:
            path = []
            while point is not None:
                path.append(point)
                point = parents[point]
            return list(reversed(path))
        for other in neighbors(point, width, height):
            if other not in parents and clear(other):
                parents[other] = point
                pending.append(other)
    raise RuntimeError("No conservative midpoint aqueduct route")


def water_plan(env, mission, anchor, radius=14):
    """Compose a connected fountain and actual source/relay supply, then roll back.

    Geometry is conservative; each action is still checked by normal construction.
    Supply and staffing activate only through ordinary future simulation ticks.
    """
    actions = []

    def frame():
        terrain, buildings, width, height = env.get_map_data()
        return exclude_hazard(terrain, mission["earthquake"], radius), buildings, width, height

    def apply(phase):
        for action in phase:
            if len(actions) >= 128:
                raise RuntimeError("Water macro exceeds 128-action bound")
            _, _, terminated, truncated, info = env.step_at(*action)
            if not info["message"].startswith("Built "):
                raise RuntimeError(info["message"])
            actions.append(action)
            if terminated or truncated:
                return True
        return False

    def reservoir(site):
        terrain, _, _, _ = frame()
        x, y = site
        clearing = [(A.CLEAR_LAND, tx, ty) for ty in range(y, y + 3) for tx in range(x, x + 3)
                    if terrain[ty, tx] & 0x11]
        return clearing + [(A.BUILD_RESERVOIR, x, y)]

    with env.snapshot() as snapshot:
        try:
            fountain = building_plan(*frame(), mission["entry"], A.BUILD_FOUNTAIN, 1, anchor=anchor)
            point = fountain[-1][1:]
            if apply(fountain):
                return actions
            supplied = [b for b in env.get_water_supply()["buildings"]
                        if b["kind"] == "reservoir" and b["water_access"]]
            if any(in_reservoir_range((b["x"], b["y"]), point) for b in supplied):
                return actions
            terrain, buildings, width, height = frame()
            sources = reservoir_sites(terrain, buildings, width, height, point)
            if not sources:
                raise RuntimeError("No clear water-adjacent reservoir footprint")
            source = next((site for site in sources if in_reservoir_range(site, point)), sources[0])
            if apply(reservoir(source)):
                return actions
            if in_reservoir_range(source, point):
                return actions
            terrain, buildings, width, height = frame()
            targets = [p for p in reservoir_sites(terrain, buildings, width, height, source, near_water=False)
                       if in_reservoir_range(p, point)]
            for target in targets[:32]:
                try:
                    path = aqueduct_route(terrain, buildings, width, height, source, target)
                except RuntimeError:
                    continue
                if len(actions) + len(path) + 1 > 128:
                    continue
                if apply(reservoir(target)):
                    return actions
                for x, y in path:
                    phase = ([(A.CLEAR_LAND, x, y)] if terrain[y, x] & 0x11 else [])
                    if not terrain[y, x] & AQUEDUCT:
                        phase.append((A.BUILD_AQUEDUCT, x, y))
                    if apply(phase):
                        return actions
                return actions
            raise RuntimeError("No bounded reservoir relay/aqueduct plan")
        finally:
            snapshot.restore()
