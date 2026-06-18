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


def _shape_bounds(block, orient_idx):
    first = True
    min_x = min_y = max_x = max_y = 0
    for layer in block["shape"][orient_idx]["layers"]:
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
    return min_x, min_y, max_x, max_y


def _first_valid_orientation(block, bay):
    shapes = block.get("shape", [])
    for orient_idx in range(len(shapes)):
        min_x, min_y, max_x, max_y = _shape_bounds(block, orient_idx)
        if max_x - min_x <= bay["width"] and max_y - min_y <= bay["height"]:
            return orient_idx, _ceil(-min_x), _ceil(-min_y)
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


def _best_fit(block, bays):
    best = None
    preferences = block.get("bay_preferences", [])
    max_preference = max(preferences) if preferences else 0
    for bay_id, bay in enumerate(bays):
        fit = _first_valid_orientation(block, bay)
        if fit is None:
            continue
        orient_idx, x, y = fit
        preference = preferences[bay_id] if bay_id < len(preferences) else 0
        candidate = (max_preference - preference, bay_id, orient_idx, x, y)
        if best is None or candidate < best:
            best = candidate
    if best is None:
        return 0, 0, 0, 0
    return best[1], best[2], best[3], best[4]


def algorithm(prob_info, timelimit=60):
    operations = {}
    current_time = 0
    bays = prob_info["bays"]

    for block_id in _block_order(prob_info):
        block = prob_info["blocks"][block_id]
        bay_id, orient_idx, x, y = _best_fit(block, bays)
        release_time = int(block.get("release_time", 0))
        processing_time = int(block.get("processing_time", 0))
        entry_time = current_time
        if release_time > entry_time:
            entry_time = release_time
        exit_time = entry_time + processing_time

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
        current_time = exit_time

    ordered = {}
    for time_key in sorted(operations, key=lambda key: int(key)):
        ops = operations[time_key]
        ops.sort(key=lambda op: 0 if op["type"] == "EXIT" else 1)
        ordered[time_key] = ops
    return {"operations": ordered}
