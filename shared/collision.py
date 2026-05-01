from __future__ import annotations

import math
from collections.abc import Iterable

from shared.models import RectState, Vec2


COLLISION_SKIN = 0.04
RESOLVE_EPSILON = 0.01


def move_circle_against_rects(pos: Vec2, delta: Vec2, radius: float, walls: Iterable[RectState]) -> None:
    wall_list = tuple(walls)
    if not wall_list:
        pos.add(delta)
        return
    resolve_circle_penetration(pos, radius, wall_list)
    distance = delta.length()
    steps = max(1, int(math.ceil(distance / max(4.0, radius * 0.35))))
    step_x = delta.x / steps
    step_y = delta.y / steps
    for _ in range(steps):
        _move_axis(pos, step_x, "x", radius, wall_list)
        _move_axis(pos, step_y, "y", radius, wall_list)
    resolve_circle_penetration(pos, radius, wall_list)


def blocked_at(pos: Vec2, radius: float, walls: Iterable[RectState]) -> bool:
    return any(circle_rect_intersects(pos, radius, wall) for wall in walls)


def circle_rect_intersects(pos: Vec2, radius: float, rect: RectState) -> bool:
    effective_radius = max(0.0, radius - COLLISION_SKIN)
    closest_x = max(rect.x, min(pos.x, rect.x + rect.w))
    closest_y = max(rect.y, min(pos.y, rect.y + rect.h))
    dx = closest_x - pos.x
    dy = closest_y - pos.y
    return dx * dx + dy * dy < effective_radius * effective_radius


def segment_rect_intersects(start: Vec2, end: Vec2, rect: RectState) -> bool:
    min_x = min(start.x, end.x)
    max_x = max(start.x, end.x)
    min_y = min(start.y, end.y)
    max_y = max(start.y, end.y)
    if max_x < rect.x or min_x > rect.x + rect.w or max_y < rect.y or min_y > rect.y + rect.h:
        return False
    if rect.contains(start) or rect.contains(end):
        return True

    dx = end.x - start.x
    dy = end.y - start.y
    t0 = 0.0
    t1 = 1.0
    for p, q in (
        (-dx, start.x - rect.x),
        (dx, rect.x + rect.w - start.x),
        (-dy, start.y - rect.y),
        (dy, rect.y + rect.h - start.y),
    ):
        if abs(p) <= 0.000001:
            if q < 0.0:
                return False
            continue
        t = q / p
        if p < 0.0:
            if t > t1:
                return False
            t0 = max(t0, t)
        else:
            if t < t0:
                return False
            t1 = min(t1, t)
    return True


def resolve_circle_penetration(pos: Vec2, radius: float, walls: Iterable[RectState]) -> None:
    wall_list = tuple(walls)
    for _ in range(4):
        moved = False
        for wall in wall_list:
            push = _circle_rect_push(pos, radius, wall)
            if push is None:
                continue
            pos.add(push)
            moved = True
        if not moved:
            return


def _move_axis(pos: Vec2, amount: float, axis: str, radius: float, walls: tuple[RectState, ...]) -> None:
    if abs(amount) <= 0.000001:
        return
    original = pos.x if axis == "x" else pos.y
    _set_axis(pos, axis, original + amount)
    if not blocked_at(pos, radius, walls):
        return
    _set_axis(pos, axis, original)

    low = 0.0
    high = 1.0
    for _ in range(10):
        mid = (low + high) * 0.5
        _set_axis(pos, axis, original + amount * mid)
        if blocked_at(pos, radius, walls):
            high = mid
        else:
            low = mid
    _set_axis(pos, axis, original + amount * low)
    if blocked_at(pos, radius, walls):
        _set_axis(pos, axis, original)


def _set_axis(pos: Vec2, axis: str, value: float) -> None:
    if axis == "x":
        pos.x = value
    else:
        pos.y = value


def _circle_rect_push(pos: Vec2, radius: float, rect: RectState) -> Vec2 | None:
    closest_x = max(rect.x, min(pos.x, rect.x + rect.w))
    closest_y = max(rect.y, min(pos.y, rect.y + rect.h))
    dx = pos.x - closest_x
    dy = pos.y - closest_y
    distance_sq = dx * dx + dy * dy
    if distance_sq >= radius * radius:
        return None
    if distance_sq > 0.000001:
        distance = math.sqrt(distance_sq)
        overlap = radius - distance + RESOLVE_EPSILON
        return Vec2(dx / distance * overlap, dy / distance * overlap)

    left = abs(pos.x - rect.x)
    right = abs(rect.x + rect.w - pos.x)
    top = abs(pos.y - rect.y)
    bottom = abs(rect.y + rect.h - pos.y)
    nearest = min(left, right, top, bottom)
    if nearest == left:
        return Vec2(-(radius + left + RESOLVE_EPSILON), 0.0)
    if nearest == right:
        return Vec2(radius + right + RESOLVE_EPSILON, 0.0)
    if nearest == top:
        return Vec2(0.0, -(radius + top + RESOLVE_EPSILON))
    return Vec2(0.0, radius + bottom + RESOLVE_EPSILON)
