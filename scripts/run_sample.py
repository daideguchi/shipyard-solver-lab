import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shipyard_solver.scoring import score_solution, validate_solution
from shipyard_solver.solver import solve_baseline

INSTANCE_PATH = ROOT / "data" / "sample_blocks.json"
OUTPUT_DIR = ROOT / "outputs"
SOLUTION_PATH = OUTPUT_DIR / "sample_solution.json"
REPORT_PATH = OUTPUT_DIR / "sample_report.md"


def render_report(instance: dict, solution: dict, metrics: dict) -> str:
    placements = solution["placements"]
    lines = [
        "# Shipyard Solver Lab — Sample Technical Report",
        "",
        "This report is generated from a toy local instance. It is not an official OGC 2026 result.",
        "",
        "## Instance",
        "",
        f"- Instance ID: `{instance['instance_id']}`",
        f"- Yards: {len(instance['yards'])}",
        f"- Blocks: {len(instance['blocks'])}",
        "",
        "## Solver",
        "",
        "- Baseline: due-date-first first-fit placement",
        "- Sort key: earliest due date, higher priority, larger area, earlier ready day",
        "- Placement search: both orientations, all yards, low-top/low-right cost",
        "",
        "## Metrics",
        "",
        f"- Score: {metrics['score']}",
        f"- Coverage: {metrics['coverage']}",
        f"- Yard utilization: {metrics['yard_utilization']}",
        f"- Placed blocks: {metrics['placed_blocks']}",
        f"- Unplaced blocks: {metrics['unplaced_blocks']}",
        f"- Weighted lateness: {metrics['weighted_lateness']}",
        "",
        "## Placements",
        "",
    ]
    for item in placements:
        lines.append(
            f"- `{item['block_id']}` -> `{item['yard_id']}` at ({item['x']}, {item['y']}) "
            f"size {item['width']}x{item['height']} rotated={item['rotated']}"
        )
    if solution.get("unplaced"):
        lines.extend(["", "## Unplaced", ""])
        for block_id in solution["unplaced"]:
            lines.append(f"- `{block_id}`")
    lines.extend(
        [
            "",
            "## Next Improvements",
            "",
            "1. Add randomized multi-start construction.",
            "2. Add relocate/swap/rotate local search.",
            "3. Add official time/resource constraints when released.",
            "4. Track every run by seed and keep the best solution archive.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    instance = json.loads(INSTANCE_PATH.read_text())
    solution = solve_baseline(instance)
    errors = validate_solution(instance, solution)
    if errors:
        raise SystemExit("\n".join(errors))
    metrics = score_solution(instance, solution)
    solution["metrics"] = metrics

    OUTPUT_DIR.mkdir(exist_ok=True)
    SOLUTION_PATH.write_text(json.dumps(solution, indent=2) + "\n")
    REPORT_PATH.write_text(render_report(instance, solution, metrics))

    print("shipyard_sample_run_ok")
    print(f"solution={SOLUTION_PATH.relative_to(ROOT)}")
    print(f"report={REPORT_PATH.relative_to(ROOT)}")
    print(f"score={metrics['score']}")


if __name__ == "__main__":
    main()
