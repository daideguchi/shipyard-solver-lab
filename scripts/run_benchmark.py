import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shipyard_solver.scoring import score_solution, validate_solution
from shipyard_solver.solver import solve_baseline, solve_constructive
from scripts.run_sample import render_report

INSTANCE_PATH = ROOT / "data" / "sample_blocks.json"
OUTPUT_DIR = ROOT / "outputs"
BENCHMARK_PATH = OUTPUT_DIR / "benchmark.json"
BEST_PATH = OUTPUT_DIR / "best_solution.json"
BEST_REPORT_PATH = OUTPUT_DIR / "best_report.md"


def run_candidate(instance: dict, solver: str, seed: int, order_mode: str = "", placement_mode: str = "") -> dict:
    if solver == "baseline":
        solution = solve_baseline(instance)
    else:
        solution = solve_constructive(instance, seed=seed, order_mode=order_mode, placement_mode=placement_mode)
    errors = validate_solution(instance, solution)
    if errors:
        return {
            "solver": solver,
            "seed": seed,
            "order_mode": order_mode,
            "placement_mode": placement_mode,
            "valid": False,
            "errors": errors,
            "score": None,
        }
    metrics = score_solution(instance, solution)
    solution["metrics"] = metrics
    return {
        "solver": solution["solver"],
        "seed": solution.get("seed", seed),
        "order_mode": solution.get("order_mode", order_mode),
        "placement_mode": solution.get("placement_mode", placement_mode),
        "valid": True,
        "score": metrics["score"],
        "metrics": metrics,
        "solution": solution,
    }


def main() -> None:
    instance = json.loads(INSTANCE_PATH.read_text())
    runs = [run_candidate(instance, "baseline", 0)]
    order_modes = ["due_date", "area_first", "priority_first", "slack_first", "randomized"]
    placement_modes = ["compact_y", "compact_x", "center"]
    for seed in range(30):
        for order_mode in order_modes:
            for placement_mode in placement_modes:
                runs.append(run_candidate(instance, "constructive", seed, order_mode, placement_mode))

    valid_runs = [run for run in runs if run["valid"]]
    best = max(valid_runs, key=lambda run: run["score"])
    public_runs = [
        {key: value for key, value in run.items() if key != "solution"}
        for run in sorted(valid_runs, key=lambda run: run["score"], reverse=True)
    ]
    benchmark = {
        "instance_id": instance["instance_id"],
        "run_count": len(runs),
        "valid_run_count": len(valid_runs),
        "best_solver": best["solver"],
        "best_seed": best["seed"],
        "best_score": best["score"],
        "runs": public_runs[:50],
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    BENCHMARK_PATH.write_text(json.dumps(benchmark, indent=2) + "\n")
    BEST_PATH.write_text(json.dumps(best["solution"], indent=2) + "\n")
    BEST_REPORT_PATH.write_text(render_report(instance, best["solution"], best["metrics"]))

    print("shipyard_benchmark_ok")
    print(f"runs={len(runs)}")
    print(f"valid={len(valid_runs)}")
    print(f"best_score={best['score']}")
    print(f"best_solver={best['solver']}")
    print(f"best_solution={BEST_PATH.relative_to(ROOT)}")
    print(f"benchmark={BENCHMARK_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

