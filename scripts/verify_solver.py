import json
import subprocess
import zipfile
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

    projection_path = ROOT / "outputs" / "official_example_projection_solution.json"
    projection_report_path = ROOT / "outputs" / "official_example_projection_report.md"
    if not projection_path.exists() or not projection_report_path.exists():
        raise SystemExit("official example projection outputs missing; run npm run official-smoke")
    projection = json.loads(projection_path.read_text())
    if projection.get("metrics", {}).get("placed_blocks") != 10:
        raise SystemExit("official example projection did not place 10 projected blocks")
    if "not official feasibility" not in projection_report_path.read_text():
        raise SystemExit("official projection report missing claim boundary")

    checker_result_path = ROOT / "outputs" / "official_checker_smoke_result.json"
    checker_report_path = ROOT / "outputs" / "official_checker_smoke_report.md"
    if not checker_result_path.exists() or not checker_report_path.exists():
        raise SystemExit("official checker smoke outputs missing; run npm run official-checker")
    checker = json.loads(checker_result_path.read_text())
    if not checker["simple_sequential"]["feasible"]:
        raise SystemExit("simple sequential official checker smoke is not feasible")
    if not checker["official_greedy_reference"]["feasible"]:
        raise SystemExit("official greedy reference is not feasible")
    if "not competitive" not in checker_report_path.read_text():
        raise SystemExit("official checker smoke report missing claim boundary")

    portfolio_result_path = ROOT / "outputs" / "official_portfolio_result.json"
    portfolio_report_path = ROOT / "outputs" / "official_portfolio_report.md"
    portfolio_solution_path = ROOT / "outputs" / "official_portfolio_solution.json"
    if not portfolio_result_path.exists() or not portfolio_report_path.exists() or not portfolio_solution_path.exists():
        raise SystemExit("official portfolio outputs missing; run npm run official-portfolio")
    portfolio = json.loads(portfolio_result_path.read_text())
    if not portfolio["official_portfolio"]["feasible"]:
        raise SystemExit("official portfolio candidate is not feasible")
    if portfolio["objective_improvement"] <= 0:
        raise SystemExit("official portfolio candidate did not improve the greedy reference")
    if not portfolio["assignment_search"]["portfolio_matches_static_bound"]:
        raise SystemExit("official portfolio candidate does not match the public-example static assignment bound")
    if "not leaderboard evidence" not in portfolio_report_path.read_text():
        raise SystemExit("official portfolio report missing claim boundary")

    package_path = ROOT / "outputs" / "official_submission_candidate.zip"
    manifest_path = ROOT / "outputs" / "official_submission_manifest.json"
    if not package_path.exists() or not manifest_path.exists():
        raise SystemExit("official submission package missing; run npm run official-package")
    with zipfile.ZipFile(package_path) as archive:
        names = set(archive.namelist())
        if names != {"myalgorithm.py"}:
            raise SystemExit(f"unexpected official package contents: {sorted(names)}")
    manifest = json.loads(manifest_path.read_text())
    if manifest["files"][0]["archive_path"] != "myalgorithm.py":
        raise SystemExit("official package manifest missing myalgorithm.py")

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
    print(f"official_projection_score={projection['metrics']['score']}")
    print(f"official_checker_objective={checker['simple_sequential']['objective']}")
    print(f"official_portfolio_objective={portfolio['official_portfolio']['objective']}")
    print(f"official_portfolio_improvement={portfolio['objective_improvement']}")
    print(f"official_portfolio_matches_static_bound={portfolio['assignment_search']['portfolio_matches_static_bound']}")
    print(f"official_submission_zip={manifest['zip_path']}")


if __name__ == "__main__":
    main()
