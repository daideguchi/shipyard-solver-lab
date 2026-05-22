from __future__ import annotations

from collections import defaultdict

from .model import Block, Placement, Yard


def parse_instance(raw: dict) -> tuple[list[Yard], list[Block]]:
    yards = [Yard(**item) for item in raw["yards"]]
    blocks = [Block(**item) for item in raw["blocks"]]
    return yards, blocks


def rectangles_overlap(a: Placement, b: Placement) -> bool:
    if a.yard_id != b.yard_id:
        return False
    return not (
        a.x + a.width <= b.x
        or b.x + b.width <= a.x
        or a.y + a.height <= b.y
        or b.y + b.height <= a.y
    )


def fits(placement: Placement, yard: Yard, placed: list[Placement]) -> bool:
    if placement.x < 0 or placement.y < 0:
        return False
    if placement.x + placement.width > yard.width:
        return False
    if placement.y + placement.height > yard.height:
        return False
    return all(not rectangles_overlap(placement, other) for other in placed)


def candidate_orientations(block: Block) -> list[tuple[int, int, bool]]:
    if block.width == block.height:
        return [(block.width, block.height, False)]
    return [(block.width, block.height, False), (block.height, block.width, True)]


def candidate_positions(yard: Yard, width: int, height: int) -> list[tuple[int, int]]:
    positions = [(0, 0)]
    for y in range(0, max(1, yard.height - height + 1)):
        for x in range(0, max(1, yard.width - width + 1)):
            if x == 0 or y == 0 or x % 2 == 0 or y % 2 == 0:
                positions.append((x, y))
    return positions


def solve_baseline(raw: dict) -> dict:
    yards, blocks = parse_instance(raw)
    placed_by_yard: dict[str, list[Placement]] = defaultdict(list)
    unplaced: list[str] = []

    ordered = sorted(
        blocks,
        key=lambda b: (b.due_day, -b.priority, -(b.width * b.height), b.ready_day),
    )

    for block in ordered:
        best: Placement | None = None
        best_cost: tuple[int, int, int, str] | None = None
        for yard in yards:
            for width, height, rotated in candidate_orientations(block):
                if width > yard.width or height > yard.height:
                    continue
                for x, y in candidate_positions(yard, width, height):
                    finish_day = block.ready_day + 1
                    candidate = Placement(
                        block_id=block.id,
                        yard_id=yard.id,
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                        start_day=block.ready_day,
                        finish_day=finish_day,
                        rotated=rotated,
                    )
                    if not fits(candidate, yard, placed_by_yard[yard.id]):
                        continue
                    top = y + height
                    right = x + width
                    lateness = max(0, finish_day - block.due_day)
                    cost = (lateness, top, right, yard.id)
                    if best is None or cost < best_cost:
                        best = candidate
                        best_cost = cost
        if best is None:
            unplaced.append(block.id)
        else:
            placed_by_yard[best.yard_id].append(best)

    placements = [p for yard_id in sorted(placed_by_yard) for p in placed_by_yard[yard_id]]
    return {
        "instance_id": raw.get("instance_id", "unknown"),
        "solver": "baseline_due_date_first_fit",
        "placements": [p.__dict__ for p in placements],
        "unplaced": unplaced,
    }

