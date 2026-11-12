"""Optional paid garden geometry; native desirability/evolution remains authoritative."""

from .baseline import NOT_CLEAR
from .env import ActionType as A


def garden_plan(terrain, buildings, width, height, anchor, radius=4, tiles=4):
    if radius <= 0 or not 1 <= tiles <= 16:
        raise RuntimeError("No bounded garden range/batch")
    hx, hy = anchor
    sites = [(x, y) for y in range(max(1, hy - radius), min(height - 1, hy + radius + 1))
             for x in range(max(1, hx - radius), min(width - 1, hx + radius + 1))
             if not buildings[y, x] and not terrain[y, x] & (NOT_CLEAR & ~0x11)]
    sites.sort(key=lambda p: (abs(p[0] - hx) + abs(p[1] - hy), p))
    if not sites:
        raise RuntimeError("No clear garden tiles near this anchor")
    actions = []
    for x, y in sites[:tiles]:
        if terrain[y, x] & 0x11:
            actions.append((A.CLEAR_LAND, x, y))
        actions.append((A.BUILD_GARDEN, x, y))
    return actions
