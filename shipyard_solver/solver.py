from __future__ import annotations

from collections import defaultdict
import random

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


def contact_positions(yard: Yard, width: int, height: int, placed: list[Placement]) -> list[tuple[int, int]]:
    xs = {0, max(0, yard.width - width)}
    ys = {0, max(0, yard.height - height)}
    for item in placed:
        xs.update({item.x, item.x + item.width, item.x - width, item.x + item.width - width})
        ys.update({item.y, item.y + item.height, item.y - height, item.y + item.height - height})
    return [
        (x, y)
        for y in sorted(value for value in ys if 0 <= value <= yard.height - height)
        for x in sorted(value for value in xs if 0 <= value <= yard.width - width)
    ]


def block_order_key(block: Block, mode: str, rng: random.Random) -> tuple:
    jitter = rng.random()
    area = block.width * block.height
    if mode == "area_first":
        return (-area, block.due_day, -block.priority, jitter)
    if mode == "priority_first":
        return (-block.priority, block.due_day, -area, jitter)
    if mode == "slack_first":
        slack = block.due_day - block.ready_day
        return (slack, -block.priority, -area, jitter)
    if mode == "randomized":
        return (jitter,)
    return (block.due_day, -block.priority, -area, block.ready_day, jitter)


def placement_cost(candidate: Placement, yard: Yard, block: Block, mode: str) -> tuple:
    top = candidate.y + candidate.height
    right = candidate.x + candidate.width
    lateness = max(0, candidate.finish_day - block.due_day)
    waste_right = yard.width - right
    waste_top = yard.height - top
    if mode == "compact_x":
        return (lateness, right, top, waste_top, yard.id)
    if mode == "compact_y":
        return (lateness, top, right, waste_right, yard.id)
    if mode == "center":
        cx = candidate.x + candidate.width / 2
        cy = candidate.y + candidate.height / 2
        center_cost = abs(cx - yard.width / 2) + abs(cy - yard.height / 2)
        return (lateness, center_cost, top, right, yard.id)
    return (lateness, top, right, yard.id)


def solution_score_value(yards: list[Yard], blocks: list[Block], placements: list[Placement], unplaced: list[str]) -> float:
    block_by_id = {block.id: block for block in blocks}
    yard_area = sum(yard.width * yard.height for yard in yards)
    placed_area = sum(placement.area for placement in placements)
    total_block_area = sum(block.width * block.height for block in blocks)
    weighted_lateness = sum(
        max(0, placement.finish_day - block_by_id[placement.block_id].due_day)
        * block_by_id[placement.block_id].priority
        for placement in placements
    )
    bounding_area = 0
    for yard in yards:
        yard_placements = [p for p in placements if p.yard_id == yard.id]
        if not yard_placements:
            continue
        bounding_area += max(p.x + p.width for p in yard_placements) * max(p.y + p.height for p in yard_placements)
    utilization = placed_area / yard_area if yard_area else 0
    coverage = placed_area / total_block_area if total_block_area else 0
    compactness = placed_area / bounding_area if bounding_area else 0
    return 1000 * coverage + 350 * utilization + 120 * compactness - 35 * weighted_lateness - 180 * len(unplaced)


def state_rank(
    yards: list[Yard],
    blocks: list[Block],
    placements: list[Placement],
    unplaced: list[str],
    rng: random.Random,
) -> tuple:
    placed_area = sum(placement.area for placement in placements)
    bounding_area = 0
    for yard in yards:
        yard_placements = [p for p in placements if p.yard_id == yard.id]
        if yard_placements:
            bounding_area += max(p.x + p.width for p in yard_placements) * max(p.y + p.height for p in yard_placements)
    block_by_id = {block.id: block for block in blocks}
    weighted_lateness = sum(
        max(0, placement.finish_day - block_by_id[placement.block_id].due_day)
        * block_by_id[placement.block_id].priority
        for placement in placements
    )
    return (len(unplaced), weighted_lateness, bounding_area - placed_area, -placed_area, rng.random())


def solve_beam_search(
    raw: dict,
    seed: int = 0,
    order_mode: str = "area_first",
    placement_mode: str = "compact_x",
    beam_width: int = 80,
) -> dict:
    yards, blocks = parse_instance(raw)
    rng = random.Random(seed)
    ordered = sorted(blocks, key=lambda b: block_order_key(b, order_mode, rng))
    states: list[tuple[list[Placement], list[str]]] = [([], [])]

    for block in ordered:
        next_states: list[tuple[list[Placement], list[str]]] = []
        for placements, unplaced in states:
            placed_by_yard: dict[str, list[Placement]] = defaultdict(list)
            for item in placements:
                placed_by_yard[item.yard_id].append(item)

            placed_any = False
            for yard in yards:
                for width, height, rotated in candidate_orientations(block):
                    if width > yard.width or height > yard.height:
                        continue
                    for x, y in contact_positions(yard, width, height, placed_by_yard[yard.id]):
                        candidate = Placement(
                            block_id=block.id,
                            yard_id=yard.id,
                            x=x,
                            y=y,
                            width=width,
                            height=height,
                            start_day=block.ready_day,
                            finish_day=block.ready_day + block.processing_time,
                            rotated=rotated,
                        )
                        if not fits(candidate, yard, placed_by_yard[yard.id]):
                            continue
                        placed_any = True
                        next_states.append((placements + [candidate], unplaced))
            if not placed_any:
                next_states.append((placements, unplaced + [block.id]))

        next_states.sort(key=lambda state: state_rank(yards, blocks, state[0], state[1], rng))
        deduped: list[tuple[list[Placement], list[str]]] = []
        seen: set[tuple] = set()
        for placements, unplaced in next_states:
            signature = tuple(
                sorted(
                    (p.block_id, p.yard_id, p.x, p.y, p.width, p.height, p.rotated)
                    for p in placements
                )
            ) + tuple(sorted(unplaced))
            if signature in seen:
                continue
            seen.add(signature)
            deduped.append((placements, unplaced))
            if len(deduped) >= beam_width:
                break
        states = deduped

    best_placements, best_unplaced = max(
        states,
        key=lambda state: solution_score_value(yards, blocks, state[0], state[1]),
    )
    return {
        "instance_id": raw.get("instance_id", "unknown"),
        "solver": f"beam_{order_mode}_{placement_mode}_w{beam_width}",
        "seed": seed,
        "order_mode": order_mode,
        "placement_mode": placement_mode,
        "beam_width": beam_width,
        "placements": [p.__dict__ for p in sorted(best_placements, key=lambda p: (p.yard_id, p.block_id))],
        "unplaced": best_unplaced,
    }


def solve_constructive(raw: dict, seed: int = 0, order_mode: str = "due_date", placement_mode: str = "compact_y") -> dict:
    yards, blocks = parse_instance(raw)
    rng = random.Random(seed)
    placed_by_yard: dict[str, list[Placement]] = defaultdict(list)
    unplaced: list[str] = []

    ordered = sorted(
        blocks,
        key=lambda b: block_order_key(b, order_mode, rng),
    )

    for block in ordered:
        best: Placement | None = None
        best_cost: tuple[int, int, int, str] | None = None
        for yard in yards:
            for width, height, rotated in candidate_orientations(block):
                if width > yard.width or height > yard.height:
                    continue
                for x, y in candidate_positions(yard, width, height):
                    candidate = Placement(
                        block_id=block.id,
                        yard_id=yard.id,
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                        start_day=block.ready_day,
                        finish_day=block.ready_day + block.processing_time,
                        rotated=rotated,
                    )
                    if not fits(candidate, yard, placed_by_yard[yard.id]):
                        continue
                    cost = placement_cost(candidate, yard, block, placement_mode)
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
        "solver": f"constructive_{order_mode}_{placement_mode}",
        "seed": seed,
        "order_mode": order_mode,
        "placement_mode": placement_mode,
        "placements": [p.__dict__ for p in placements],
        "unplaced": unplaced,
    }


def solve_baseline(raw: dict) -> dict:
    solution = solve_constructive(raw, seed=0, order_mode="due_date", placement_mode="compact_y")
    solution["solver"] = "baseline_due_date_first_fit"
    return solution
