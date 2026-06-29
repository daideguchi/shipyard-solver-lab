# myalgorithm.py
# OGC 2026 official-safe standalone fallback.
#
# The official system only extracts myalgorithm.py from the submitted zip.
# Therefore this file must not depend on any local helper module. This
# conservative version schedules one block at a time in an official
# operations-format solution. It is intentionally simple: first get a
# non-exception, checker-shaped result into the official evaluator.


def _ceil(value):
    integer = int(value)
    if value > integer:
        return integer + 1
    return integer


def _floor(value):
    integer = int(value)
    if value < integer:
        return integer - 1
    return integer


def _orientation_geometry(block, orient_idx):
    layers = []
    for layer in block["shape"][orient_idx]["layers"]:
        if layer:
            layers.append(layer)
    if not layers:
        return 0, 0, 0, 0, 1, 1

    ref_x = layers[0][0][0]
    ref_y = layers[0][0][1]
    first = True
    min_x = min_y = max_x = max_y = 0
    for layer in layers:
        for point in layer:
            x = point[0]
            y = point[1]
            if first:
                min_x = max_x = x
                min_y = max_y = y
                first = False
            else:
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y
    return ref_x, ref_y, min_x, min_y, max_x, max_y


def _placement_bounds(block, orient_idx, bay):
    ref_x, ref_y, min_x, min_y, max_x, max_y = _orientation_geometry(block, orient_idx)
    left = min_x - ref_x
    right = max_x - ref_x
    bottom = min_y - ref_y
    top = max_y - ref_y
    min_place_x = _ceil(-left)
    max_place_x = _floor(bay["width"] - right)
    min_place_y = _ceil(-bottom)
    max_place_y = _floor(bay["height"] - top)
    return min_place_x, max_place_x, min_place_y, max_place_y


def _bbox_offsets(block, orient_idx):
    ref_x, ref_y, min_x, min_y, max_x, max_y = _orientation_geometry(block, orient_idx)
    return min_x - ref_x, min_y - ref_y, max_x - ref_x, max_y - ref_y


def _bbox_at(block, orient_idx, x, y):
    left, bottom, right, top = _bbox_offsets(block, orient_idx)
    return x + left, y + bottom, x + right, y + top


def _bbox_overlap(left, right):
    margin = 0.000001
    return (
        left[0] < right[2] + margin
        and right[0] < left[2] + margin
        and left[1] < right[3] + margin
        and right[1] < left[3] + margin
    )


def _first_valid_orientation(block, bay):
    shapes = block.get("shape", [])
    for orient_idx in range(len(shapes)):
        min_place_x, max_place_x, min_place_y, max_place_y = _placement_bounds(block, orient_idx, bay)
        if min_place_x <= max_place_x and min_place_y <= max_place_y:
            return orient_idx, min_place_x, min_place_y
    return None


def _block_order(prob_info):
    indexed = []
    for idx, block in enumerate(prob_info["blocks"]):
        preferences = block.get("bay_preferences", [0])
        best_preference = max(preferences) if preferences else 0
        indexed.append(
            (
                block.get("due_date", 0),
                block.get("release_time", 0),
                block.get("processing_time", 0),
                -best_preference,
                idx,
            )
        )
    indexed.sort()
    return [item[-1] for item in indexed]


def _candidate_orders(prob_info):
    blocks = prob_info["blocks"]
    orders = [
        _block_order(prob_info),
        sorted(
            range(len(blocks)),
            key=lambda idx: (
                blocks[idx].get("due_date", 0),
                blocks[idx].get("processing_time", 0),
                blocks[idx].get("release_time", 0),
                idx,
            ),
        ),
        sorted(
            range(len(blocks)),
            key=lambda idx: (
                blocks[idx].get("due_date", 0)
                - blocks[idx].get("release_time", 0)
                - blocks[idx].get("processing_time", 0),
                blocks[idx].get("due_date", 0),
                idx,
            ),
        ),
        sorted(
            range(len(blocks)),
            key=lambda idx: (
                blocks[idx].get("release_time", 0),
                blocks[idx].get("due_date", 0),
                idx,
            ),
        ),
        sorted(
            range(len(blocks)),
            key=lambda idx: (
                -blocks[idx].get("workload", 0),
                blocks[idx].get("due_date", 0),
                idx,
            ),
        ),
        sorted(
            range(len(blocks)),
            key=lambda idx: (
                -blocks[idx].get("processing_time", 0),
                blocks[idx].get("due_date", 0),
                idx,
            ),
        ),
        sorted(
            range(len(blocks)),
            key=lambda idx: (
                blocks[idx].get("due_date", 0),
                -blocks[idx].get("workload", 0),
                idx,
            ),
        ),
        sorted(
            range(len(blocks)),
            key=lambda idx: (
                blocks[idx].get("release_time", 0) + blocks[idx].get("processing_time", 0),
                blocks[idx].get("due_date", 0),
                idx,
            ),
        ),
    ]
    unique = []
    seen = set()
    for order in orders:
        signature = tuple(order)
        if signature in seen:
            continue
        seen.add(signature)
        unique.append(order)
    return unique


def _preference(block, bay_id):
    preferences = block.get("bay_preferences", [])
    if bay_id < len(preferences):
        return preferences[bay_id]
    return 0


def _time_overlaps(entry, exit_time, other_entry, other_exit):
    return entry < other_exit and other_entry < exit_time


def _bay_weights(bays):
    areas = []
    for bay in bays:
        areas.append(bay["width"] * bay["height"])
    avg_area = sum(areas) / len(areas) if areas else 1
    return [avg_area / area if area else 1 for area in areas]


def _imbalance_after(bay_loads, bay_weights, bay_id, workload):
    if len(bay_loads) < 2:
        return 0
    max_gap = 0
    for left in range(len(bay_loads)):
        left_load = bay_loads[left]
        if left == bay_id:
            left_load += workload
        for right in range(len(bay_loads)):
            if left == right:
                continue
            right_load = bay_loads[right]
            if right == bay_id:
                right_load += workload
            gap = bay_weights[left] * left_load - bay_weights[right] * right_load
            if gap < 0:
                gap = -gap
            if gap > max_gap:
                max_gap = gap
    return max_gap


def _empty_entry(placements, release_time, processing_time):
    entry = release_time
    changed = True
    while changed:
        changed = False
        exit_time = entry + processing_time
        for placement in placements:
            if _time_overlaps(entry, exit_time, placement["entry_time"], placement["exit_time"]):
                if placement["exit_time"] > entry:
                    entry = placement["exit_time"]
                    changed = True
    return entry


def _active_placements(placements, entry_time, exit_time):
    active = []
    for placement in placements:
        if _time_overlaps(entry_time, exit_time, placement["entry_time"], placement["exit_time"]):
            active.append(placement)
    return active


def _candidate_entries(placements, release_time):
    entries = {release_time}
    for placement in placements:
        if placement["exit_time"] >= release_time:
            entries.add(placement["exit_time"])
    return sorted(entries)


def _candidate_positions(block, orient_idx, bay, active):
    min_x, max_x, min_y, max_y = _placement_bounds(block, orient_idx, bay)
    left, bottom, right, top = _bbox_offsets(block, orient_idx)
    xs = {min_x}
    ys = {min_y}
    xs.add(max_x)
    ys.add(max_y)
    for placement in active:
        bbox = placement["bbox"]
        xs.add(_floor(bbox[0] - right))
        xs.add(_ceil(bbox[2] - left))
        xs.add(_ceil(bbox[2] - left + 0.000001))
        ys.add(_floor(bbox[1] - top))
        ys.add(_ceil(bbox[3] - bottom))
        ys.add(_ceil(bbox[3] - bottom + 0.000001))
    valid_xs = [x for x in sorted(xs) if min_x <= x <= max_x]
    valid_ys = [y for y in sorted(ys) if min_y <= y <= max_y]
    return valid_xs[:60], valid_ys[:60]


def _best_fit(block, bays, placements_by_bay, bay_loads, weights):
    best = None
    preferences = block.get("bay_preferences", [])
    max_preference = max(preferences) if preferences else 0
    if preferences:
        bay_count = len(preferences)
    else:
        bay_count = len(bays)
    if bay_count > len(bays):
        bay_count = len(bays)

    bay_weights = _bay_weights(bays)
    release_time = _ceil(block.get("release_time", 0))
    processing_time = max(1, _ceil(block.get("processing_time", 1)))
    due_date = block.get("due_date", 0)
    workload = block.get("workload", 0)
    w1 = weights.get("w1", 1)
    w2 = weights.get("w2", 1)
    w3 = weights.get("w3", 1)

    for bay_id in range(bay_count):
        bay = bays[bay_id]
        preference = _preference(block, bay_id)
        preference_penalty = max_preference - preference
        placements = placements_by_bay[bay_id]
        for orient_idx in range(len(block.get("shape", []))):
            bounds = _placement_bounds(block, orient_idx, bay)
            if bounds[0] > bounds[1] or bounds[2] > bounds[3]:
                continue
            for entry_time in _candidate_entries(placements, release_time):
                exit_time = entry_time + processing_time
                active = _active_placements(placements, entry_time, exit_time)
                xs, ys = _candidate_positions(block, orient_idx, bay, active)
                for x in xs:
                    for y in ys:
                        bbox = _bbox_at(block, orient_idx, x, y)
                        blocked = False
                        for placement in active:
                            if _bbox_overlap(bbox, placement["bbox"]):
                                blocked = True
                                break
                        if blocked:
                            continue
                        tardiness = exit_time - due_date
                        if tardiness < 0:
                            tardiness = 0
                        imbalance = _imbalance_after(bay_loads, bay_weights, bay_id, workload)
                        balance_weight = w2
                        score = w1 * tardiness + balance_weight * imbalance + w3 * preference_penalty
                        candidate = (
                            score,
                            exit_time,
                            preference_penalty,
                            len(active),
                            bay_id,
                            orient_idx,
                            x,
                            y,
                            entry_time,
                            bbox,
                        )
                        if best is None or candidate < best:
                            best = candidate
    if best is None:
        for bay_id in range(bay_count):
            fit = _first_valid_orientation(block, bays[bay_id])
            if fit is None:
                continue
            orient_idx, x, y = fit
            entry_time = _empty_entry(placements_by_bay[bay_id], release_time, processing_time)
            exit_time = entry_time + processing_time
            return bay_id, orient_idx, x, y, entry_time, exit_time, _bbox_at(block, orient_idx, x, y)
        return 0, 0, 0, 0, release_time, release_time + processing_time, _bbox_at(block, 0, 0, 0)
    return best[4], best[5], best[6], best[7], best[8], best[1], best[9]


def _score_assignments(prob_info, assignments, bay_loads):
    bays = prob_info["bays"]
    weights = prob_info.get("weights", {})
    w1 = weights.get("w1", 1)
    w2 = weights.get("w2", 1)
    w3 = weights.get("w3", 1)
    obj1 = 0
    obj3 = 0
    for assignment in assignments:
        block = prob_info["blocks"][assignment["block_id"]]
        tardiness = assignment["exit_time"] - block.get("due_date", 0)
        if tardiness > 0:
            obj1 += tardiness
        preferences = block.get("bay_preferences", [])
        if preferences:
            obj3 += max(preferences) - _preference(block, assignment["bay_id"])
    bay_weights = _bay_weights(bays)
    obj2 = 0
    if len(bays) >= 2:
        for left in range(len(bays)):
            for right in range(len(bays)):
                if left == right:
                    continue
                gap = bay_weights[left] * bay_loads[left] - bay_weights[right] * bay_loads[right]
                if gap < 0:
                    gap = -gap
                if gap > obj2:
                    obj2 = gap
    return w1 * obj1 + w2 * obj2 + w3 * obj3


def _ordered_operations(operations):
    ordered = {}
    for time_key in sorted(operations, key=lambda key: int(key)):
        ops = operations[time_key]
        ops.sort(key=lambda op: 0 if op["type"] == "EXIT" else 1)
        ordered[time_key] = ops
    return ordered


def _build_for_order(prob_info, order):
    operations = {}
    bays = prob_info["bays"]
    placements_by_bay = [[] for _ in bays]
    bay_loads = [0 for _ in bays]
    weights = prob_info.get("weights", {})
    assignments = []

    for block_id in order:
        block = prob_info["blocks"][block_id]
        bay_id, orient_idx, x, y, entry_time, exit_time, bbox = _best_fit(
            block, bays, placements_by_bay, bay_loads, weights
        )

        entry_key = str(entry_time)
        exit_key = str(exit_time)
        if entry_key not in operations:
            operations[entry_key] = []
        if exit_key not in operations:
            operations[exit_key] = []

        operations[entry_key].append(
            {
                "type": "ENTRY",
                "block_id": block_id,
                "bay_id": bay_id,
                "x": x,
                "y": y,
                "orient_idx": orient_idx,
            }
        )
        operations[exit_key].append(
            {
                "type": "EXIT",
                "block_id": block_id,
                "bay_id": bay_id,
            }
        )
        if bay_id < len(placements_by_bay):
            placements_by_bay[bay_id].append(
                {
                    "block_id": block_id,
                    "entry_time": entry_time,
                    "exit_time": exit_time,
                    "bbox": bbox,
                }
            )
            bay_loads[bay_id] += block.get("workload", 0)
            assignments.append(
                {
                    "block_id": block_id,
                    "bay_id": bay_id,
                    "entry_time": entry_time,
                    "exit_time": exit_time,
                }
            )

    return _ordered_operations(operations), _score_assignments(prob_info, assignments, bay_loads)


def algorithm(prob_info, timelimit=60):
    best_operations = None
    best_score = None
    for order in _candidate_orders(prob_info):
        operations, score = _build_for_order(prob_info, order)
        if best_score is None or score < best_score:
            best_score = score
            best_operations = operations
    return {"operations": best_operations if best_operations is not None else {}}
