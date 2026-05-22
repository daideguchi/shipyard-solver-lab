from __future__ import annotations

from .model import Placement, Yard
from .solver import rectangles_overlap


def load_placements(solution: dict) -> list[Placement]:
    return [Placement(**item) for item in solution["placements"]]


def validate_solution(instance: dict, solution: dict) -> list[str]:
    yards = {item["id"]: Yard(**item) for item in instance["yards"]}
    placements = load_placements(solution)
    errors: list[str] = []

    seen = set()
    for placement in placements:
        if placement.block_id in seen:
            errors.append(f"duplicate placement for {placement.block_id}")
        seen.add(placement.block_id)
        yard = yards.get(placement.yard_id)
        if yard is None:
            errors.append(f"unknown yard {placement.yard_id} for {placement.block_id}")
            continue
        if placement.x + placement.width > yard.width or placement.y + placement.height > yard.height:
            errors.append(f"out of bounds: {placement.block_id}")

    for idx, left in enumerate(placements):
        for right in placements[idx + 1 :]:
            if rectangles_overlap(left, right):
                errors.append(f"overlap: {left.block_id} and {right.block_id} in {left.yard_id}")

    block_ids = {item["id"] for item in instance["blocks"]}
    missing = block_ids - seen - set(solution.get("unplaced", []))
    for block_id in sorted(missing):
        errors.append(f"missing decision for {block_id}")

    return errors


def score_solution(instance: dict, solution: dict) -> dict:
    placements = load_placements(solution)
    block_by_id = {item["id"]: item for item in instance["blocks"]}
    yard_area = sum(item["width"] * item["height"] for item in instance["yards"])
    placed_area = sum(placement.area for placement in placements)
    total_block_area = sum(item["width"] * item["height"] for item in instance["blocks"])
    unplaced = len(solution.get("unplaced", []))

    weighted_lateness = 0
    for placement in placements:
        block = block_by_id[placement.block_id]
        weighted_lateness += max(0, placement.finish_day - block["due_day"]) * block.get("priority", 1)

    utilization = placed_area / yard_area if yard_area else 0
    coverage = placed_area / total_block_area if total_block_area else 0
    bounding_area = 0
    for yard in instance["yards"]:
        yard_placements = [p for p in placements if p.yard_id == yard["id"]]
        if not yard_placements:
            continue
        max_x = max(p.x + p.width for p in yard_placements)
        max_y = max(p.y + p.height for p in yard_placements)
        bounding_area += max_x * max_y
    compactness = placed_area / bounding_area if bounding_area else 0
    score = round(1000 * coverage + 350 * utilization + 120 * compactness - 35 * weighted_lateness - 180 * unplaced, 2)

    return {
        "score": score,
        "coverage": round(coverage, 4),
        "yard_utilization": round(utilization, 4),
        "packing_compactness": round(compactness, 4),
        "placed_blocks": len(placements),
        "unplaced_blocks": unplaced,
        "weighted_lateness": weighted_lateness,
    }
