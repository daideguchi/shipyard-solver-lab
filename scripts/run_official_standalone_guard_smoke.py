import importlib.util
import json
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
RESULT_PATH = OUTPUT_DIR / "official_standalone_guard_result.json"
REPORT_PATH = OUTPUT_DIR / "official_standalone_guard_report.md"


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


def rect(x0: float, y0: float, x1: float, y1: float) -> list[list[float]]:
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def base_instance(name: str, blocks: list[dict]) -> dict:
    return {
        "name": name,
        "bays": [{"width": 10, "height": 10}],
        "blocks": blocks,
        "weights": {"w1": 1.0, "w2": 1.0, "w3": 1.0},
    }


def fractional_time_case() -> dict:
    return base_instance(
        "standalone_fractional_time_guard",
        [
            {
                "release_time": 0.2,
                "due_date": 10,
                "processing_time": 1.2,
                "workload": 1,
                "bay_preferences": [1],
                "shape": [{"orientation": 0, "layers": [rect(0, 0, 2, 2)]}],
            }
        ],
    )


def integer_position_case() -> dict:
    return base_instance(
        "standalone_integer_position_guard",
        [
            {
                "release_time": 0,
                "due_date": 10,
                "processing_time": 1,
                "workload": 1,
                "bay_preferences": [1],
                "shape": [
                    {"orientation": 0, "layers": [rect(-0.2, 0, 9.2, 2)]},
                    {"orientation": 1, "layers": [rect(0, 0, 9, 2)]},
                ],
            }
        ],
    )


def first_entry(solution: dict) -> dict:
    for _, operations in sorted(solution["operations"].items(), key=lambda item: int(item[0])):
        for operation in operations:
            if operation["type"] == "ENTRY":
                return operation
    raise RuntimeError("solution has no ENTRY operation")


def run_case(module, check_feasibility, instance: dict) -> dict:
    solution = module.algorithm(instance, timelimit=10)
    result = check_feasibility(instance, solution)
    entry = first_entry(solution)
    if not result.get("feasible"):
        raise SystemExit(f"{instance['name']} infeasible: {json.dumps(result, indent=2)}")
    return {
        "name": instance["name"],
        "feasible": result["feasible"],
        "stage": result["stage"],
        "objective": result["objective"],
        "entry": entry,
        "operations": solution["operations"],
    }


def write_report(payload: dict) -> None:
    lines = [
        "# Official Standalone Guard Smoke Report",
        "",
        "This report targets hidden-instance risk in the single-file fallback algorithm.",
        "",
        "## Guards",
        "",
    ]
    for case in payload["cases"]:
        lines.append(f"- `{case['name']}`: feasible={case['feasible']} stage={case['stage']} entry={case['entry']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These are small synthetic guard cases. They do not claim leaderboard quality.",
            "They verify that the submitted single-file algorithm handles fractional timing and skips an orientation that cannot be placed at any integer coordinate inside the bay.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    zip_path = fetch_baseline_zip()
    with tempfile.TemporaryDirectory(prefix="ogc2026-standalone-guard-") as tmp:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(tmp)
        base = Path(tmp) / "ogc2026"
        sys.path.insert(0, str(base / "baseline"))
        from utils import check_feasibility  # type: ignore

        module = load_myalgorithm()
        public_example = json.loads((base / "alg_tester" / "example" / "example_B2_b10.json").read_text())
        cases = [
            run_case(module, check_feasibility, public_example),
            run_case(module, check_feasibility, fractional_time_case()),
            run_case(module, check_feasibility, integer_position_case()),
        ]

    if cases[1]["entry"]["orient_idx"] != 0:
        raise SystemExit(f"fractional timing guard selected unexpected orientation: {cases[1]['entry']}")
    if cases[2]["entry"]["orient_idx"] != 1:
        raise SystemExit(f"integer position guard did not skip invalid orientation: {cases[2]['entry']}")

    payload = {
        "source": BASELINE_URL,
        "boundary": "single-file fallback guard only; not leaderboard evidence",
        "all_cases_feasible": all(item["feasible"] for item in cases),
        "cases": cases,
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_report(payload)

    print("official_standalone_guard_smoke_ok")
    print(f"cases={len(cases)}")
    print(f"all_cases_feasible={payload['all_cases_feasible']}")
    print(f"report={REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
