import json
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shipyard_solver.scoring import score_solution, validate_solution


def main() -> None:
    subprocess.run(["python3", "scripts/run_sample.py"], cwd=ROOT, check=True)
    subprocess.run(["python3", "scripts/run_benchmark.py"], cwd=ROOT, check=True)

    instance = json.loads((ROOT / "data" / "sample_blocks.json").read_text())
    solution = json.loads((ROOT / "outputs" / "sample_solution.json").read_text())
    errors = validate_solution(instance, solution)
    if errors:
        raise SystemExit("\n".join(errors))
    metrics = score_solution(instance, solution)

    expected_blocks = len(instance["blocks"])
    if metrics["placed_blocks"] + metrics["unplaced_blocks"] != expected_blocks:
        raise SystemExit("block accounting mismatch")
    if metrics["placed_blocks"] < 10:
        raise SystemExit("baseline placed too few blocks")
    if metrics["score"] <= 0:
        raise SystemExit("baseline score should be positive on toy instance")
    benchmark = json.loads((ROOT / "outputs" / "benchmark.json").read_text())
    if benchmark["valid_run_count"] < 900:
        raise SystemExit("benchmark did not run enough valid candidates")
    if benchmark["best_score"] < metrics["score"]:
        raise SystemExit("benchmark best score is worse than baseline")

    report = (ROOT / "outputs" / "sample_report.md").read_text()
    required = [
        "Sample Technical Report",
        "Baseline: due-date-first first-fit placement",
        "Next Improvements",
    ]
    for marker in required:
        if marker not in report:
            raise SystemExit(f"missing report marker: {marker}")

    print("shipyard_solver_verify_ok")
    print(f"score={metrics['score']}")
    print(f"placed_blocks={metrics['placed_blocks']}")
    print(f"benchmark_best={benchmark['best_score']}")


if __name__ == "__main__":
    main()
