"""OGC 2026 candidate algorithm.

This file is intentionally shaped like the organizer template:

    def algorithm(prob_info: dict, timelimit: float) -> dict

It runs the public greedy baseline first, then spends remaining time on a
small portfolio search over bay assignments. Every candidate is checked with
the official feasibility checker, and only a strictly better feasible solution
replaces the baseline.
"""

from __future__ import annotations

import contextlib
import copy
import io
import itertools
import time

import baseline_greedy
from utils import Bay, Block, check_feasibility


def _bay_assignment_bound(prob_info: dict, bay_count: int) -> int:
    block_count = len(prob_info["blocks"])
    if bay_count <= 1:
        return 1
    if block_count <= 12:
        return bay_count ** block_count
    if block_count <= 16:
        return min(5000, bay_count ** block_count)
    return 1200


def _static_assignment_score(prob_info: dict, assignment: tuple[int, ...]) -> float:
    blocks = prob_info["blocks"]
    bays = prob_info["bays"]
    weights = prob_info.get("weights", {})
    w2 = weights.get("w2", 1.0)
    w3 = weights.get("w3", 1.0)

    bay_areas = [bay["width"] * bay["height"] for bay in bays]
    avg_area = sum(bay_areas) / len(bay_areas)
    bay_weights = [avg_area / area for area in bay_areas]
    loads = [0.0] * len(bays)
    preference_penalty = 0.0

    for block_id, bay_id in enumerate(assignment):
        block = blocks[block_id]
        loads[bay_id] += block["workload"]
        preference_penalty += max(block["bay_preferences"]) - block["bay_preferences"][bay_id]

    if len(bays) >= 2:
        imbalance = max(
            abs(bay_weights[left] * loads[left] - bay_weights[right] * loads[right])
            for left in range(len(bays))
            for right in range(len(bays))
            if left != right
        )
    else:
        imbalance = 0.0

    return w2 * imbalance + w3 * preference_penalty


def _seed_assignments(prob_info: dict, greedy_solution: dict) -> set[tuple[int, ...]]:
    block_count = len(prob_info["blocks"])
    bay_count = len(prob_info["bays"])
    seeds: set[tuple[int, ...]] = set()

    greedy_assignment = [0] * block_count
    for ops in greedy_solution.get("operations", {}).values():
        for op in ops:
            if op.get("type") == "ENTRY":
                greedy_assignment[op["block_id"]] = op["bay_id"]
    seeds.add(tuple(greedy_assignment))

    preference_assignment = tuple(
        max(range(bay_count), key=lambda bay_id: block["bay_preferences"][bay_id])
        for block in prob_info["blocks"]
    )
    seeds.add(preference_assignment)

    for base in list(seeds):
        for block_id in range(block_count):
            for bay_id in range(bay_count):
                if bay_id == base[block_id]:
                    continue
                changed = list(base)
                changed[block_id] = bay_id
                seeds.add(tuple(changed))

    return seeds


def _candidate_assignments(prob_info: dict, greedy_solution: dict) -> list[tuple[int, ...]]:
    bay_count = len(prob_info["bays"])
    block_count = len(prob_info["blocks"])
    limit = _bay_assignment_bound(prob_info, bay_count)

    if bay_count ** block_count <= limit:
        candidates = itertools.product(range(bay_count), repeat=block_count)
    else:
        candidates = _seed_assignments(prob_info, greedy_solution)

    return sorted(candidates, key=lambda assignment: _static_assignment_score(prob_info, assignment))[:limit]


def _build_operations(assignments: dict[int, dict]) -> dict:
    return baseline_greedy._build_operations(list(assignments.values()))


def _place_fixed_assignment(prob_info: dict, assignment: tuple[int, ...], deadline: float) -> dict | None:
    blocks = prob_info["blocks"]
    bays = [Bay.from_dict(item, idx) for idx, item in enumerate(prob_info["bays"])]
    bay_placed: list[list[Block]] = [[] for _ in bays]
    bay_schedule: list[list[tuple[int, int]]] = [[] for _ in bays]
    assignments: dict[int, dict] = {}
    order = sorted(range(len(blocks)), key=lambda idx: (blocks[idx]["due_date"], blocks[idx]["processing_time"]))

    for block_id in order:
        if time.time() > deadline:
            return None
        block = blocks[block_id]
        bay_id = assignment[block_id]
        bay = bays[bay_id]
        best = None

        for orient_idx in range(len(block["shape"])):
            bbox = baseline_greedy._block_bbox(block, orient_idx)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            if width > bay.width + 1e-6 or height > bay.height + 1e-6:
                continue

            candidates = baseline_greedy._candidate_positions(
                bay.width, bay.height, bay_placed[bay_id], bbox
            )
            for x, y in candidates:
                new_block = Block(block_id=block_id, block_data=block, x=x, y=y, orient_idx=orient_idx)
                if not bay.contains_block(new_block):
                    continue

                entry, exit_time = baseline_greedy._find_earliest_slot(
                    new_block,
                    bay,
                    bay_placed[bay_id],
                    bay_schedule[bay_id],
                    block["release_time"],
                    block["processing_time"],
                )
                if entry is None:
                    continue

                tardiness = max(0, exit_time - block["due_date"])
                score = (tardiness, exit_time, y + bbox[3], x + bbox[2], orient_idx)
                if best is None or score < best[0]:
                    best = (score, new_block, x, y, orient_idx, entry, exit_time)

        if best is None:
            return None

        _, placed_block, x, y, orient_idx, entry, exit_time = best
        bay_placed[bay_id].append(placed_block)
        bay_schedule[bay_id].append((entry, exit_time))
        assignments[block_id] = {
            "block_id": block_id,
            "bay_id": bay_id,
            "x": int(round(x)),
            "y": int(round(y)),
            "orient_idx": orient_idx,
            "entry_time": int(round(entry)),
            "exit_time": int(round(exit_time)),
        }

    return {"operations": _build_operations(assignments)}


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    start = time.time()
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet):
        best_solution = baseline_greedy.greedyalgorithm(prob_info, timelimit=max(1.0, timelimit * 0.35))
    best_result = check_feasibility(prob_info, best_solution)

    deadline = start + max(0.25, timelimit * 0.94)
    for assignment in _candidate_assignments(prob_info, best_solution):
        if time.time() > deadline:
            break
        candidate = _place_fixed_assignment(prob_info, assignment, deadline)
        if candidate is None:
            continue
        result = check_feasibility(prob_info, candidate)
        if not result.get("feasible"):
            continue
        if not best_result.get("feasible") or result["objective"] < best_result["objective"]:
            best_solution = copy.deepcopy(candidate)
            best_result = result

    return best_solution
