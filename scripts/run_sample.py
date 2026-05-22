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
    solver_name = solution.get("solver", "baseline_due_date_first_fit")
    if solver_name.startswith("beam_"):
        solver_lines = [
            f"- Solver: `{solver_name}`",
            f"- Seed: {solution.get('seed')}",
            f"- Order mode: `{solution.get('order_mode')}`",
            f"- Placement mode: `{solution.get('placement_mode')}`",
            f"- Beam width: {solution.get('beam_width')}",
            "- Search: keeps the best partial layouts at each block step, using contact-point placements, rotation, yard reassignment, overlap checks, and compactness-aware ranking",
        ]
    elif solver_name.startswith("constructive_"):
        solver_lines = [
            f"- Solver: `{solver_name}`",
            f"- Seed: {solution.get('seed')}",
            f"- Order mode: `{solution.get('order_mode')}`",
            f"- Placement mode: `{solution.get('placement_mode')}`",
            "- Search: randomized constructive placement across both orientations and all yards",
        ]
    else:
        solver_lines = [
            "- Baseline: due-date-first first-fit placement",
            "- Sort key: earliest due date, higher priority, larger area, earlier ready day",
            "- Placement search: both orientations, all yards, low-top/low-right cost",
        ]
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
        *solver_lines,
        "",
        "## Metrics",
        "",
        f"- Score: {metrics['score']}",
        f"- Coverage: {metrics['coverage']}",
        f"- Yard utilization: {metrics['yard_utilization']}",
        f"- Packing compactness: {metrics.get('packing_compactness', 'n/a')}",
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
            "1. Match the official OGC input/output schema as soon as problem files are released.",
            "2. Add relocate, swap, rotate, and yard-reassignment local search on top of the beam output.",
            "3. Add official time, resource, crane, and precedence constraints when released.",
            "4. Track every run by seed, beam width, score, and validation errors.",
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
