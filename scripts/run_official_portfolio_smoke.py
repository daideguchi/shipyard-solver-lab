import contextlib
import importlib.util
import io
import json
import re
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
BASELINE_URL = "https://www.optichallenge.com/assets/baseline-latest-BtM0fjcU.zip"
ZIP_PATH = OUTPUT_DIR / "official_baseline_latest.zip"
MYALGORITHM_PATH = ROOT / "official_submission" / "myalgorithm.py"
SOLUTION_PATH = OUTPUT_DIR / "official_portfolio_solution.json"
RESULT_PATH = OUTPUT_DIR / "official_portfolio_result.json"
REPORT_PATH = OUTPUT_DIR / "official_portfolio_report.md"


def fetch_baseline_zip() -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    if not ZIP_PATH.exists():
        urllib.request.urlretrieve(BASELINE_URL, ZIP_PATH)
    return ZIP_PATH


def load_myalgorithm():
    spec = importlib.util.spec_from_file_location("candidate_myalgorithm", MYALGORITHM_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {MYALGORITHM_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_report(payload: dict) -> None:
    portfolio = payload["official_portfolio"]
    greedy = payload["official_greedy_reference"]
    delta = payload["objective_delta_vs_greedy"]
    assignment = payload["assignment_search"]
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Official Portfolio Smoke Report",
                "",
                "This report uses the public OGC 2026 baseline package and official feasibility checker.",
                "",
                "## Candidate Algorithm",
                "",
                "- File: `official_submission/myalgorithm.py`",
                "- Method: run the public greedy baseline, then search bay-assignment candidates and keep the best feasible official solution.",
                f"- Feasible: {portfolio['feasible']}",
                f"- Stage: {portfolio['stage']}",
                f"- Objective: {portfolio['objective']}",
                f"- obj1 tardiness: {portfolio['obj1']}",
                f"- obj2 imbalance: {portfolio['obj2']}",
                f"- obj3 preference penalty: {portfolio['obj3']}",
                "",
                "## Public Greedy Reference",
                "",
                f"- Feasible: {greedy['feasible']}",
                f"- Stage: {greedy['stage']}",
                f"- Objective: {greedy['objective']}",
                f"- obj1 tardiness: {greedy['obj1']}",
                f"- obj2 imbalance: {greedy['obj2']}",
                f"- obj3 preference penalty: {greedy['obj3']}",
                "",
                "## Delta",
                "",
                f"- Objective delta vs greedy: {delta}",
                f"- Improvement: {payload['objective_improvement']}",
                "",
                "## Assignment Search Proof",
                "",
                f"- Candidate assignments evaluated: {assignment['candidate_count']}",
                f"- Exhaustive for this example: {assignment['exhaustive']}",
                f"- Best static assignment objective: {assignment['best_static_objective']}",
                f"- Portfolio matches static bound: {assignment['portfolio_matches_static_bound']}",
                "",
                "## Boundary",
                "",
                "This is an official-example smoke test, not leaderboard evidence.",
                "It proves that the repository now contains a checker-validated official-format algorithm candidate that improves over the public greedy reference on example_B2_b10.",
                "The static-bound statement is only for this small public example, where all bay assignments are enumerable.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def normalized_log_head(text: str) -> list[str]:
    return [re.sub(r"\s+\d+\.\d+s$", "  <elapsed>", line) for line in text.splitlines()[:14]]


def main() -> None:
    zip_path = fetch_baseline_zip()
    with tempfile.TemporaryDirectory(prefix="ogc2026-portfolio-") as tmp:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(tmp)
        base = Path(tmp) / "ogc2026"
        sys.path.insert(0, str(base / "baseline"))

        import baseline_greedy  # type: ignore
        from utils import check_feasibility  # type: ignore

        prob_info = json.loads((base / "alg_tester" / "example" / "example_B2_b10.json").read_text())

        greedy_log = io.StringIO()
        with contextlib.redirect_stdout(greedy_log):
            greedy_solution = baseline_greedy.greedyalgorithm(prob_info, timelimit=10)
        greedy_result = check_feasibility(prob_info, greedy_solution)
        if not greedy_result.get("feasible"):
            raise SystemExit(json.dumps(greedy_result, indent=2))

        module = load_myalgorithm()
        candidate_assignments = module._candidate_assignments(prob_info, greedy_solution)
        static_scores = [module._static_assignment_score(prob_info, item) for item in candidate_assignments]
        best_static = min(static_scores)
        exhaustive_count = len(prob_info["bays"]) ** len(prob_info["blocks"])
        exhaustive = len(candidate_assignments) == exhaustive_count

        candidate_solution = module.algorithm(prob_info, timelimit=10)
        candidate_result = check_feasibility(prob_info, candidate_solution)
        if not candidate_result.get("feasible"):
            raise SystemExit(json.dumps(candidate_result, indent=2))

        delta = candidate_result["objective"] - greedy_result["objective"]
        if delta >= -1e-6:
            raise SystemExit(
                f"official portfolio did not improve greedy: candidate={candidate_result['objective']} greedy={greedy_result['objective']}"
            )

        payload = {
            "source": BASELINE_URL,
            "example": prob_info.get("name"),
            "boundary": "official example smoke only; not leaderboard evidence",
            "official_portfolio": candidate_result,
            "official_greedy_reference": greedy_result,
            "objective_delta_vs_greedy": round(delta, 6),
            "objective_improvement": round(-delta, 6),
            "assignment_search": {
                "candidate_count": len(candidate_assignments),
                "exhaustive": exhaustive,
                "exhaustive_count": exhaustive_count,
                "best_static_objective": round(best_static, 6),
                "portfolio_matches_static_bound": (
                    exhaustive
                    and abs(candidate_result["objective"] - best_static) < 1e-6
                    and candidate_result["obj1"] == 0
                ),
            },
            "greedy_log_head": normalized_log_head(greedy_log.getvalue()),
        }

    SOLUTION_PATH.write_text(json.dumps(candidate_solution, indent=2) + "\n", encoding="utf-8")
    RESULT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_report(payload)

    print("official_portfolio_smoke_ok")
    print(f"portfolio_feasible={candidate_result['feasible']}")
    print(f"portfolio_objective={candidate_result['objective']:.6f}")
    print(f"greedy_objective={greedy_result['objective']:.6f}")
    print(f"objective_improvement={payload['objective_improvement']:.6f}")
    print(f"assignment_candidates={payload['assignment_search']['candidate_count']}")
    print(f"portfolio_matches_static_bound={payload['assignment_search']['portfolio_matches_static_bound']}")
    print(f"report={REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
