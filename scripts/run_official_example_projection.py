import json
from pathlib import Path
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_sample import render_report
from shipyard_solver.official_adapter import project_official_instance
from shipyard_solver.scoring import score_solution, validate_solution
from shipyard_solver.solver import solve_baseline, solve_beam_search

BASELINE_URL = "https://www.optichallenge.com/assets/baseline-latest-BtM0fjcU.zip"
OUTPUT_DIR = ROOT / "outputs"
ZIP_PATH = OUTPUT_DIR / "official_baseline_latest.zip"
PROJECTION_INSTANCE_PATH = OUTPUT_DIR / "official_example_projection_instance.json"
PROJECTION_SOLUTION_PATH = OUTPUT_DIR / "official_example_projection_solution.json"
PROJECTION_REPORT_PATH = OUTPUT_DIR / "official_example_projection_report.md"


def fetch_baseline_zip() -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    if not ZIP_PATH.exists():
        urllib.request.urlretrieve(BASELINE_URL, ZIP_PATH)
    return ZIP_PATH


def load_official_example(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path) as archive:
        with archive.open("ogc2026/alg_tester/example/example_B2_b10.json") as handle:
            return json.loads(handle.read().decode("utf-8"))


def render_projection_report(instance: dict, solution: dict, metrics: dict, baseline_metrics: dict) -> str:
    base_report = render_report(instance, solution, metrics)
    header = "\n".join(
        [
            "# Official OGC Example Projection Smoke Test",
            "",
            "This report uses the public OGC 2026 baseline package example instance.",
            "It projects official polygon/layer block data into this lab's rectangle model.",
            "That proves schema ingestion, but it is not official OGC feasibility or leaderboard scoring.",
            "",
            "## Projection Boundary",
            "",
            f"- {instance['projection_boundary']}",
            f"- Projected bays: {len(instance['yards'])}",
            f"- Projected blocks: {len(instance['blocks'])}",
            f"- Baseline projection score: {baseline_metrics['score']}",
            f"- Beam projection score: {metrics['score']}",
            f"- Projection delta: {round(metrics['score'] - baseline_metrics['score'], 2)}",
            "",
            "## Generated Lab Report",
            "",
        ]
    )
    return header + base_report


def main() -> None:
    official = load_official_example(fetch_baseline_zip())
    instance = project_official_instance(official)
    baseline = solve_baseline(instance)
    baseline_errors = validate_solution(instance, baseline)
    if baseline_errors:
        raise SystemExit("\n".join(baseline_errors))
    baseline_metrics = score_solution(instance, baseline)

    solution = solve_beam_search(
        instance,
        seed=0,
        order_mode="area_first",
        placement_mode="compact_y",
        beam_width=80,
    )
    errors = validate_solution(instance, solution)
    if errors:
        raise SystemExit("\n".join(errors))
    metrics = score_solution(instance, solution)
    solution["metrics"] = metrics
    solution["baseline_projection_score"] = baseline_metrics["score"]
    solution["projection_boundary"] = instance["projection_boundary"]

    OUTPUT_DIR.mkdir(exist_ok=True)
    PROJECTION_INSTANCE_PATH.write_text(json.dumps(instance, indent=2) + "\n")
    PROJECTION_SOLUTION_PATH.write_text(json.dumps(solution, indent=2) + "\n")
    PROJECTION_REPORT_PATH.write_text(render_projection_report(instance, solution, metrics, baseline_metrics))

    print("official_example_projection_ok")
    print(f"official_name={official.get('name')}")
    print(f"projected_blocks={len(instance['blocks'])}")
    print(f"baseline_score={baseline_metrics['score']}")
    print(f"beam_score={metrics['score']}")
    print(f"delta={round(metrics['score'] - baseline_metrics['score'], 2)}")
    print(f"report={PROJECTION_REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
