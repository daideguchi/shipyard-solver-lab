from __future__ import annotations

import math
from typing import Any


def layer_bounds(layers: list[list[list[float]]]) -> tuple[float, float, float, float]:
    vertices = [point for layer in layers for point in layer]
    if not vertices:
        return 0.0, 0.0, 1.0, 1.0
    xs = [point[0] for point in vertices]
    ys = [point[1] for point in vertices]
    return min(xs), min(ys), max(xs), max(ys)


def orientation_size(orientation: dict[str, Any]) -> tuple[int, int]:
    min_x, min_y, max_x, max_y = layer_bounds(orientation.get("layers", []))
    width = max(1, math.ceil(max_x - min_x))
    height = max(1, math.ceil(max_y - min_y))
    return width, height


def choose_projection_size(block: dict[str, Any]) -> tuple[int, int, int]:
    sizes = [
        (idx, *orientation_size(orientation))
        for idx, orientation in enumerate(block.get("shape", []))
    ]
    if not sizes:
        return 0, 1, 1
    orient_idx, width, height = min(sizes, key=lambda item: (item[1] * item[2], max(item[1], item[2])))
    return orient_idx, width, height


def project_official_instance(raw: dict[str, Any]) -> dict[str, Any]:
    """Project an official OGC polygon/layer instance into the lab's rectangle model.

    This is only a schema-ingestion smoke test. It is not an official OGC
    feasibility model because crane-path layer collisions and official scoring
    remain in the official baseline package.
    """
    yards = [
        {
            "id": f"bay_{idx}",
            "width": int(bay["width"]),
            "height": int(bay["height"]),
            "crane_capacity": 1,
        }
        for idx, bay in enumerate(raw.get("bays", []))
    ]
    blocks = []
    projection = []
    for idx, block in enumerate(raw.get("blocks", [])):
        orient_idx, width, height = choose_projection_size(block)
        projected = {
            "id": f"block_{idx}",
            "width": width,
            "height": height,
            "ready_day": int(block.get("release_time", 0)),
            "due_day": int(block.get("due_date", 0)),
            "processing_time": max(1, int(block.get("processing_time", 1))),
            "priority": max(1, int(round(float(block.get("workload", 1))))),
        }
        blocks.append(projected)
        projection.append(
            {
                "block_id": projected["id"],
                "official_index": idx,
                "chosen_orientation": orient_idx,
                "projected_size": [width, height],
                "release_time": projected["ready_day"],
                "due_date": projected["due_day"],
                "processing_time": projected["processing_time"],
                "workload": projected["priority"],
            }
        )

    return {
        "instance_id": raw.get("name", "official_projection"),
        "projection_boundary": (
            "Official OGC polygon/layer data projected to rectangles for schema-ingestion smoke testing only; "
            "not official feasibility or leaderboard scoring."
        ),
        "yards": yards,
        "blocks": blocks,
        "official_projection": projection,
    }
