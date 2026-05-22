import contextlib
import io
import json
import math
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
BASELINE_URL = "https://www.optichallenge.com/assets/baseline-latest-BtM0fjcU.zip"
ZIP_PATH = OUTPUT_DIR / "official_baseline_latest.zip"
SMOKE_SOLUTION_PATH = OUTPUT_DIR / "official_checker_smoke_solution.json"
SMOKE_RESULT_PATH = OUTPUT_DIR / "official_checker_smoke_result.json"
REPORT_PATH = OUTPUT_DIR / "official_checker_smoke_report.md"


def fetch_baseline_zip() -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    if not ZIP_PATH.exists():
        urllib.request.urlretrieve(BASELINE_URL, ZIP_PATH)
    return ZIP_PATH


def shape_bounds(block: dict, orient_idx: int) -> tuple[float, float, float, float]:
    vertices = [point for layer in block["shape"][orient_idx]["layers"] for point in layer]
    xs = [point[0] for point in vertices]
    ys = [point[1] for point in vertices]
    return min(xs), min(ys), max(xs), max(ys)


def first_valid_orientation(block: dict, bay: dict) -> tuple[int, int, int] | None:
    for orient_idx in range(len(block.get("shape", []))):
        min_x, min_y, max_x, max_y = shape_bounds(block, orient_idx)
        if max_x - min_x <= bay["width"] and max_y - min_y <= bay["height"]:
            return orient_idx, math.ceil(-min_x), math.ceil(-min_y)
    return None


def simple_sequential_solution(prob_info: dict) -> dict:
    """Build a deliberately conservative official-format solution.

    Only one block is present at a time, so crane entry/exit and collision
    feasibility are easy to verify with the official checker. This is a smoke
    test for the submission format, not a competitive objective strategy.
    """
    operations: dict[str, list[dict]] = {}
    current_time = 0
    block_order = sorted(
        range(len(prob_info["blocks"])),
        key=lambda idx: (
            prob_info["blocks"][idx]["due_date"],
            prob_info["blocks"][idx]["processing_time"],
            -max(prob_info["blocks"][idx].get("bay_preferences", [0])),
        ),
    )

    for block_id in block_order:
        block = prob_info["blocks"][block_id]
        best: tuple[int, int, int, int] | None = None
        for bay_id, bay in enumerate(prob_info["bays"]):
            fit = first_valid_orientation(block, bay)
            if fit is None:
                continue
            orient_idx, x, y = fit
            preference_penalty = max(block["bay_preferences"]) - block["bay_preferences"][bay_id]
            candidate = (preference_penalty, bay_id, orient_idx, x, y)
            if best is None or candidate < best:
                best = candidate
        if best is None:
            raise RuntimeError(f"no bay/orientation fit found for block {block_id}")

        _, bay_id, orient_idx, x, y = best
        entry_time = max(current_time, int(block["release_time"]))
        exit_time = entry_time + int(block["processing_time"])
        operations.setdefault(str(entry_time), []).append(
            {
                "type": "ENTRY",
                "block_id": block_id,
                "bay_id": bay_id,
                "x": x,
                "y": y,
                "orient_idx": orient_idx,
            }
        )
        operations.setdefault(str(exit_time), []).append(
            {"type": "EXIT", "block_id": block_id, "bay_id": bay_id}
        )
        current_time = exit_time

    for ops in operations.values():
        ops.sort(key=lambda op: 0 if op["type"] == "EXIT" else 1)
    return {"operations": dict(sorted(operations.items(), key=lambda item: int(item[0])))}


def write_report(payload: dict) -> None:
    smoke = payload["simple_sequential"]
    greedy = payload["official_greedy_reference"]
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Official Checker Smoke Report",
                "",
                "This report uses the public OGC 2026 baseline package and the official feasibility checker.",
                "",
                "## Simple Sequential Submission",
                "",
                "- Purpose: prove exact official solution format and checker integration.",
                f"- Feasible: {smoke['feasible']}",
                f"- Stage: {smoke['stage']}",
                f"- Objective: {smoke['objective']}",
                f"- obj1 tardiness: {smoke['obj1']}",
                f"- obj2 imbalance: {smoke['obj2']}",
                f"- obj3 preference penalty: {smoke['obj3']}",
                "",
                "## Official Greedy Reference",
                "",
                "- Purpose: provide a public baseline from the organizer package.",
                f"- Feasible: {greedy['feasible']}",
                f"- Stage: {greedy['stage']}",
                f"- Objective: {greedy['objective']}",
                f"- obj1 tardiness: {greedy['obj1']}",
                f"- obj2 imbalance: {greedy['obj2']}",
                f"- obj3 preference penalty: {greedy['obj3']}",
                "",
                "## Boundary",
                "",
                "The simple sequential solution is not competitive. It is intentionally conservative.",
                "The next real scoring step is to replace it with an optimized official-format algorithm while keeping the official checker green.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    zip_path = fetch_baseline_zip()
    with tempfile.TemporaryDirectory(prefix="ogc2026-baseline-") as tmp:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(tmp)
        base = Path(tmp) / "ogc2026"
        sys.path.insert(0, str(base / "baseline"))
        import baseline_greedy  # type: ignore
        from utils import check_feasibility  # type: ignore

        prob_info = json.loads((base / "alg_tester" / "example" / "example_B2_b10.json").read_text())

        simple_solution = simple_sequential_solution(prob_info)
        simple_result = check_feasibility(prob_info, simple_solution)
        if not simple_result.get("feasible"):
            raise SystemExit(json.dumps(simple_result, indent=2))

        greedy_log = io.StringIO()
        with contextlib.redirect_stdout(greedy_log):
            greedy_solution = baseline_greedy.greedyalgorithm(prob_info, timelimit=10)
        greedy_result = check_feasibility(prob_info, greedy_solution)
        if not greedy_result.get("feasible"):
            raise SystemExit(json.dumps(greedy_result, indent=2))

        payload = {
            "source": BASELINE_URL,
            "example": prob_info.get("name"),
            "boundary": "official checker smoke only; simple sequential solution is not competitive",
            "simple_sequential": simple_result,
            "official_greedy_reference": greedy_result,
            "objective_gap_vs_greedy": round(simple_result["objective"] - greedy_result["objective"], 6),
            "greedy_log_head": greedy_log.getvalue().splitlines()[:14],
        }

    SMOKE_SOLUTION_PATH.write_text(json.dumps(simple_solution, indent=2) + "\n", encoding="utf-8")
    SMOKE_RESULT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_report(payload)

    print("official_checker_smoke_ok")
    print(f"simple_feasible={simple_result['feasible']}")
    print(f"simple_objective={simple_result['objective']:.6f}")
    print(f"greedy_feasible={greedy_result['feasible']}")
    print(f"greedy_objective={greedy_result['objective']:.6f}")
    print(f"objective_gap_vs_greedy={payload['objective_gap_vs_greedy']:.6f}")
    print(f"report={REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
