import contextlib
import copy
import importlib.util
import io
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
RESULT_PATH = OUTPUT_DIR / "official_deep_robustness_probe.json"
REPORT_PATH = OUTPUT_DIR / "official_deep_robustness_probe.md"


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


def make_variant(base_instance: dict, block_count: int, bay_count: int, due_offset: int) -> dict:
    instance = copy.deepcopy(base_instance)
    if bay_count == 3:
        instance["bays"] = copy.deepcopy(base_instance["bays"]) + [{"width": 78, "height": 21}]
    else:
        instance["bays"] = copy.deepcopy(base_instance["bays"])

    blocks = []
    for index in range(block_count):
        source = copy.deepcopy(base_instance["blocks"][index % len(base_instance["blocks"])])
        wave = index // len(base_instance["blocks"])
        source["release_time"] = int(source.get("release_time", 0) + wave * 3 + (index % 2))
        source["due_date"] = int(source.get("due_date", 0) + wave * 4 + due_offset)
        source["processing_time"] = max(1, int(source.get("processing_time", 1)))
        source["workload"] = max(1, int(source.get("workload", 1) + (index % 4) * 4))
        preferences = list(source["bay_preferences"])
        if bay_count == 3:
            preferences.append(max(1, int((preferences[0] + preferences[1]) / 2 + ((index % 5) - 2) * 5)))
        source["bay_preferences"] = preferences[:bay_count]
        blocks.append(source)

    instance["blocks"] = blocks
    instance["name"] = f"deep_B{bay_count}_b{block_count}_due{due_offset:+d}"
    return instance


def write_report(payload: dict) -> None:
    lines = [
        "# Official Deep Robustness Probe",
        "",
        "This is an internal regression probe built from the public OGC baseline example.",
        "It is not leaderboard evidence and does not replace the official hidden evaluator.",
        "",
        "## Summary",
        "",
        f"- Variants: {payload['variant_count']}",
        f"- All candidate feasible: {payload['all_candidates_feasible']}",
        f"- All candidate match/improve greedy: {payload['all_candidates_match_or_improve_greedy']}",
        f"- Improved variants: {payload['improved_count']}",
        f"- Worst delta vs greedy: {payload['worst_delta_vs_greedy']}",
        f"- Best improvement vs greedy: {payload['best_improvement_vs_greedy']}",
        "",
        "## Variants",
        "",
        "| Variant | Greedy | Candidate | Delta | Feasible |",
        "|---|---:|---:|---:|---|",
    ]
    for item in payload["variants"]:
        lines.append(
            "| {name} | {greedy:.6f} | {candidate:.6f} | {delta:.6f} | {feasible} |".format(
                name=item["name"],
                greedy=item["greedy_objective"],
                candidate=item["candidate_objective"],
                delta=item["objective_delta_vs_greedy"],
                feasible=item["candidate_feasible"],
            )
        )
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    zip_path = fetch_baseline_zip()
    with tempfile.TemporaryDirectory(prefix="ogc2026-deep-robustness-") as tmp:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(tmp)
        base = Path(tmp) / "ogc2026"
        sys.path.insert(0, str(base / "baseline"))

        import baseline_greedy  # type: ignore
        from utils import check_feasibility  # type: ignore

        raw = json.loads((base / "alg_tester" / "example" / "example_B2_b10.json").read_text())
        module = load_myalgorithm()
        variants = []

        block_counts = [10, 12, 14, 16, 18, 20, 24, 28, 32, 36]
        due_offsets = [-3, 2]
        for bay_count in [2, 3]:
            for due_offset in due_offsets:
                for block_count in block_counts:
                    instance = make_variant(raw, block_count=block_count, bay_count=bay_count, due_offset=due_offset)
                    greedy_log = io.StringIO()
                    with contextlib.redirect_stdout(greedy_log):
                        greedy_solution = baseline_greedy.greedyalgorithm(instance, timelimit=5)
                    greedy_result = check_feasibility(instance, greedy_solution)
                    if not greedy_result.get("feasible"):
                        raise SystemExit(f"greedy infeasible on {instance['name']}: {greedy_result}")

                    candidate_solution = module.algorithm(instance, timelimit=10)
                    candidate_result = check_feasibility(instance, candidate_solution)
                    if not candidate_result.get("feasible"):
                        raise SystemExit(f"candidate infeasible on {instance['name']}: {candidate_result}")
                    delta = candidate_result["objective"] - greedy_result["objective"]
                    if delta > 1e-6:
                        raise SystemExit(
                            f"candidate worse than greedy on {instance['name']}: "
                            f"candidate={candidate_result['objective']} greedy={greedy_result['objective']}"
                        )
                    variants.append(
                        {
                            "name": instance["name"],
                            "blocks": block_count,
                            "bays": bay_count,
                            "due_offset": due_offset,
                            "candidate_feasible": candidate_result["feasible"],
                            "candidate_objective": candidate_result["objective"],
                            "greedy_objective": greedy_result["objective"],
                            "objective_delta_vs_greedy": round(delta, 6),
                            "objective_improvement": round(-delta, 6),
                        }
                    )

    deltas = [item["objective_delta_vs_greedy"] for item in variants]
    improvements = [item["objective_improvement"] for item in variants]
    payload = {
        "source": BASELINE_URL,
        "boundary": "internal public-example-derived robustness probe only; not leaderboard evidence",
        "variant_count": len(variants),
        "all_candidates_feasible": all(item["candidate_feasible"] for item in variants),
        "all_candidates_match_or_improve_greedy": all(item["objective_delta_vs_greedy"] <= 0 for item in variants),
        "improved_count": sum(1 for item in variants if item["objective_delta_vs_greedy"] < -1e-6),
        "worst_delta_vs_greedy": max(deltas),
        "best_improvement_vs_greedy": max(improvements),
        "variants": variants,
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_report(payload)

    print("official_deep_robustness_probe_ok")
    print(f"variants={payload['variant_count']}")
    print(f"all_candidates_feasible={payload['all_candidates_feasible']}")
    print(f"all_candidates_match_or_improve_greedy={payload['all_candidates_match_or_improve_greedy']}")
    print(f"improved_count={payload['improved_count']}")
    print(f"worst_delta_vs_greedy={payload['worst_delta_vs_greedy']:.6f}")
    print(f"best_improvement_vs_greedy={payload['best_improvement_vs_greedy']:.6f}")
    print(f"report={REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
