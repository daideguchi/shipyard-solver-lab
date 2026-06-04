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
import random
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


def _partial_assignment_score(
    prob_info: dict,
    loads: tuple[float, ...],
    preference_penalty: float,
) -> float:
    bays = prob_info["bays"]
    weights = prob_info.get("weights", {})
    w2 = weights.get("w2", 1.0)
    w3 = weights.get("w3", 1.0)
    bay_areas = [bay["width"] * bay["height"] for bay in bays]
    avg_area = sum(bay_areas) / len(bay_areas)
    bay_weights = [avg_area / area for area in bay_areas]

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


def _ordered_blocks_for_assignment(prob_info: dict) -> list[int]:
    blocks = prob_info["blocks"]
    return sorted(
        range(len(blocks)),
        key=lambda block_id: (
            -blocks[block_id]["workload"],
            blocks[block_id]["due_date"],
            blocks[block_id]["release_time"],
            block_id,
        ),
    )


def _beam_assignment_candidates(
    prob_info: dict,
    beam_width: int = 160,
    max_results: int = 1200,
) -> list[tuple[int, ...]]:
    """Return static-score candidates without enumerating bay_count**block_count."""
    blocks = prob_info["blocks"]
    bay_count = len(prob_info["bays"])
    order = _ordered_blocks_for_assignment(prob_info)
    states: list[tuple[float, tuple[int | None, ...], tuple[float, ...], float]] = [
        (0.0, tuple([None] * len(blocks)), tuple([0.0] * bay_count), 0.0)
    ]

    for block_id in order:
        block = blocks[block_id]
        expanded = []
        best_pref = max(block["bay_preferences"])
        for _, partial, loads, pref_penalty in states:
            for bay_id in range(bay_count):
                next_partial = list(partial)
                next_partial[block_id] = bay_id
                next_loads = list(loads)
                next_loads[bay_id] += block["workload"]
                next_pref = pref_penalty + best_pref - block["bay_preferences"][bay_id]
                score = _partial_assignment_score(prob_info, tuple(next_loads), next_pref)
                expanded.append((score, tuple(next_partial), tuple(next_loads), next_pref))
        expanded.sort(key=lambda item: item[0])
        deduped = []
        seen = set()
        for item in expanded:
            signature = item[1]
            if signature in seen:
                continue
            seen.add(signature)
            deduped.append(item)
            if len(deduped) >= beam_width:
                break
        states = deduped

    complete = [tuple(value for value in partial if value is not None) for _, partial, _, _ in states]
    complete.sort(key=lambda assignment: _static_assignment_score(prob_info, assignment))
    return complete[:max_results]


def _improve_assignment_static(
    prob_info: dict,
    assignment: tuple[int, ...],
    max_rounds: int = 4,
) -> tuple[int, ...]:
    bay_count = len(prob_info["bays"])
    current = assignment
    current_score = _static_assignment_score(prob_info, current)

    for _ in range(max_rounds):
        improved = False
        best_assignment = current
        best_score = current_score

        for block_id in _ordered_blocks_for_assignment(prob_info):
            for bay_id in range(bay_count):
                if bay_id == current[block_id]:
                    continue
                candidate = list(current)
                candidate[block_id] = bay_id
                candidate = tuple(candidate)
                score = _static_assignment_score(prob_info, candidate)
                if score + 1e-9 < best_score:
                    best_assignment = candidate
                    best_score = score

        if best_assignment == current:
            for left in range(len(current)):
                for right in range(left + 1, len(current)):
                    if current[left] == current[right]:
                        continue
                    candidate = list(current)
                    candidate[left], candidate[right] = candidate[right], candidate[left]
                    candidate = tuple(candidate)
                    score = _static_assignment_score(prob_info, candidate)
                    if score + 1e-9 < best_score:
                        best_assignment = candidate
                        best_score = score

        if best_assignment != current:
            current = best_assignment
            current_score = best_score
            improved = True

        if not improved:
            break

    return current


def _random_assignment_candidates(
    prob_info: dict,
    count: int,
    seed: int = 20260524,
) -> list[tuple[int, ...]]:
    rng = random.Random(seed)
    blocks = prob_info["blocks"]
    bay_count = len(prob_info["bays"])
    candidates = []
    for _ in range(count):
        assignment = []
        for block in blocks:
            if rng.random() < 0.72:
                assignment.append(max(range(bay_count), key=lambda bay_id: block["bay_preferences"][bay_id]))
            else:
                assignment.append(rng.randrange(bay_count))
        candidates.append(tuple(assignment))
    return candidates


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

    seeds.update(_constructive_seed_assignments(prob_info))
    return seeds


def _constructive_seed_assignments(prob_info: dict) -> set[tuple[int, ...]]:
    """Build deterministic static-score seeds for larger instances."""
    blocks = prob_info["blocks"]
    bay_count = len(prob_info["bays"])
    if bay_count <= 1:
        return {tuple([0] * len(blocks))}

    order_specs = [
        sorted(range(len(blocks)), key=lambda idx: (-blocks[idx]["workload"], blocks[idx]["due_date"], idx)),
        sorted(range(len(blocks)), key=lambda idx: (blocks[idx]["due_date"], -blocks[idx]["workload"], idx)),
        sorted(range(len(blocks)), key=lambda idx: (blocks[idx]["release_time"], blocks[idx]["due_date"], idx)),
        sorted(
            range(len(blocks)),
            key=lambda idx: (
                -(max(blocks[idx]["bay_preferences"]) - min(blocks[idx]["bay_preferences"])),
                -blocks[idx]["workload"],
                idx,
            ),
        ),
    ]
    seeds: set[tuple[int, ...]] = set()

    for order in order_specs:
        assignment: list[int | None] = [None] * len(blocks)
        loads = [0.0] * bay_count
        preference_penalty = 0.0
        for block_id in order:
            block = blocks[block_id]
            best_pref = max(block["bay_preferences"])
            best_choice = None
            for bay_id in range(bay_count):
                next_loads = list(loads)
                next_loads[bay_id] += block["workload"]
                next_pref = preference_penalty + best_pref - block["bay_preferences"][bay_id]
                score = _partial_assignment_score(prob_info, tuple(next_loads), next_pref)
                choice = (score, next_pref, -block["bay_preferences"][bay_id], bay_id)
                if best_choice is None or choice < best_choice:
                    best_choice = choice
            chosen_bay = best_choice[-1]
            assignment[block_id] = chosen_bay
            loads[chosen_bay] += block["workload"]
            preference_penalty += best_pref - block["bay_preferences"][chosen_bay]

        seeds.add(tuple(int(item) for item in assignment if item is not None))

    return seeds


def _candidate_assignments(prob_info: dict, greedy_solution: dict) -> list[tuple[int, ...]]:
    bay_count = len(prob_info["bays"])
    block_count = len(prob_info["blocks"])
    limit = _bay_assignment_bound(prob_info, bay_count)

    if bay_count ** block_count <= limit:
        candidates = itertools.product(range(bay_count), repeat=block_count)
    else:
        seeded = _seed_assignments(prob_info, greedy_solution)
        beam = _beam_assignment_candidates(prob_info, beam_width=180, max_results=limit)
        random_count = max(120, limit // 5)
        random_candidates = _random_assignment_candidates(prob_info, count=random_count)
        candidates = set(seeded)
        candidates.update(beam)
        candidates.update(random_candidates)
        ordered = sorted(candidates, key=lambda item: _static_assignment_score(prob_info, item))
        candidates.update(_improve_assignment_static(prob_info, item) for item in ordered[: limit * 2])

    return sorted(candidates, key=lambda assignment: _static_assignment_score(prob_info, assignment))[:limit]


def _assignment_from_solution(prob_info: dict, solution: dict) -> tuple[int, ...] | None:
    block_count = len(prob_info["blocks"])
    assignment: list[int | None] = [None] * block_count

    for ops in solution.get("operations", {}).values():
        for op in ops:
            if op.get("type") != "ENTRY":
                continue
            block_id = op.get("block_id")
            bay_id = op.get("bay_id")
            if not isinstance(block_id, int) or not isinstance(bay_id, int):
                return None
            if not (0 <= block_id < block_count):
                return None
            assignment[block_id] = bay_id

    if any(item is None for item in assignment):
        return None
    return tuple(int(item) for item in assignment)


def _neighbor_assignments(
    prob_info: dict,
    assignment: tuple[int, ...],
    max_results: int = 420,
) -> list[tuple[int, ...]]:
    """Small objective-driven neighborhood around the current best assignment."""
    bay_count = len(prob_info["bays"])
    if bay_count <= 1:
        return []

    ordered_blocks = _ordered_blocks_for_assignment(prob_info)
    candidates: set[tuple[int, ...]] = set()

    for block_id in ordered_blocks:
        for bay_id in range(bay_count):
            if bay_id == assignment[block_id]:
                continue
            changed = list(assignment)
            changed[block_id] = bay_id
            candidates.add(tuple(changed))

    for left_index, left in enumerate(ordered_blocks):
        for right in ordered_blocks[left_index + 1 :]:
            if assignment[left] == assignment[right]:
                continue
            swapped = list(assignment)
            swapped[left], swapped[right] = swapped[right], swapped[left]
            candidates.add(tuple(swapped))

    improved = {_improve_assignment_static(prob_info, item, max_rounds=2) for item in candidates}
    candidates.update(improved)
    candidates.discard(assignment)

    return sorted(candidates, key=lambda item: _static_assignment_score(prob_info, item))[:max_results]


def _placement_orders(prob_info: dict) -> list[list[int]]:
    blocks = prob_info["blocks"]
    order_specs = [
        lambda idx: (blocks[idx]["due_date"], blocks[idx]["processing_time"], -blocks[idx]["workload"], idx),
        lambda idx: (blocks[idx]["release_time"], blocks[idx]["due_date"], -blocks[idx]["workload"], idx),
        lambda idx: (-blocks[idx]["workload"], blocks[idx]["due_date"], blocks[idx]["release_time"], idx),
        lambda idx: (blocks[idx]["due_date"] - blocks[idx]["release_time"], -blocks[idx]["workload"], idx),
    ]
    orders = []
    seen = set()
    for key in order_specs:
        order = tuple(sorted(range(len(blocks)), key=key))
        if order in seen:
            continue
        seen.add(order)
        orders.append(list(order))
    return orders


def _build_operations(assignments: dict[int, dict]) -> dict:
    return baseline_greedy._build_operations(list(assignments.values()))


def _place_fixed_assignment(
    prob_info: dict,
    assignment: tuple[int, ...],
    deadline: float,
    order: list[int] | None = None,
) -> dict | None:
    blocks = prob_info["blocks"]
    bays = [Bay.from_dict(item, idx) for idx, item in enumerate(prob_info["bays"])]
    bay_placed: list[list[Block]] = [[] for _ in bays]
    bay_schedule: list[list[tuple[int, int]]] = [[] for _ in bays]
    assignments: dict[int, dict] = {}
    if order is None:
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
                score = (tardiness, exit_time, y + bbox[3], x + bbox[2], abs((x + bbox[2]) - bay.width), orient_idx)
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
    orders = _placement_orders(prob_info)
    seen_assignments: set[tuple[int, ...]] = set()

    for assignment in _candidate_assignments(prob_info, best_solution):
        seen_assignments.add(assignment)
        if time.time() > deadline:
            break
        for order in orders:
            if time.time() > deadline:
                break
            candidate = _place_fixed_assignment(prob_info, assignment, deadline, order=order)
            if candidate is None:
                continue
            result = check_feasibility(prob_info, candidate)
            if not result.get("feasible"):
                continue
            if not best_result.get("feasible") or result["objective"] < best_result["objective"]:
                best_solution = copy.deepcopy(candidate)
                best_result = result

    best_assignment = _assignment_from_solution(prob_info, best_solution)
    if best_assignment is not None:
        seen_assignments.add(best_assignment)

    neighborhood_rounds = 0
    while best_assignment is not None and time.time() <= deadline and neighborhood_rounds < 2:
        neighborhood_rounds += 1
        improved = False
        for assignment in _neighbor_assignments(prob_info, best_assignment):
            if time.time() > deadline:
                break
            if assignment in seen_assignments:
                continue
            seen_assignments.add(assignment)
            for order in orders:
                if time.time() > deadline:
                    break
                candidate = _place_fixed_assignment(prob_info, assignment, deadline, order=order)
                if candidate is None:
                    continue
                result = check_feasibility(prob_info, candidate)
                if not result.get("feasible"):
                    continue
                if result["objective"] < best_result["objective"]:
                    best_solution = copy.deepcopy(candidate)
                    best_result = result
                    best_assignment = assignment
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break

    return best_solution
