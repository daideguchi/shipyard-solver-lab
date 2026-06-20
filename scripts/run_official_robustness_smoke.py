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
RESULT_PATH = OUTPUT_DIR / "official_robustness_result.json"
REPORT_PATH = OUTPUT_DIR / "official_robustness_report.md"


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


def make_variant(base_instance: dict, block_count: int, bay_count: int) -> dict:
    instance = copy.deepcopy(base_instance)
    if bay_count == 3:
        instance["bays"] = copy.deepcopy(base_instance["bays"]) + [{"width": 78, "height": 21}]
    else:
        instance["bays"] = copy.deepcopy(base_instance["bays"])

    blocks = []
    for index in range(block_count):
        source = copy.deepcopy(base_instance["blocks"][index % len(base_instance["blocks"])])
        wave = index // len(base_instance["blocks"])
        source["release_time"] = int(source.get("release_time", 0) + wave * 3)
        source["due_date"] = int(source.get("due_date", 0) + wave * 4 + 2)
        source["processing_time"] = max(1, int(source.get("processing_time", 1)))
        source["workload"] = max(1, int(source.get("workload", 1) + (index % 3) * 5))
        preferences = list(source["bay_preferences"])
        if bay_count == 3:
            preferences.append(max(1, int((preferences[0] + preferences[1]) / 2 + ((index % 4) - 1) * 7)))
        source["bay_preferences"] = preferences[:bay_count]
        blocks.append(source)

    instance["blocks"] = blocks
    instance["name"] = f"synthetic_B{bay_count}_b{block_count}"
    return instance


def write_report(payload: dict) -> None:
    lines = [
        "# Official Robustness Smoke Report",
        "",
        "This report uses deterministic synthetic variants derived from the public OGC baseline example.",
        "",
        "It is not official leaderboard evidence. It checks whether the standalone candidate stays feasible and matches or improves the public greedy reference when the public example is expanded in size.",
        "",
        "## Results",
        "",
        "| Variant | Blocks | Bays | Greedy objective | Candidate objective | Delta vs greedy | Match or better | Candidate feasible |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for item in payload["variants"]:
        lines.append(
            "| {name} | {blocks} | {bays} | {greedy:.6f} | {candidate:.6f} | {delta:.6f} | {match_or_better} | {feasible} |".format(
                name=item["name"],
                blocks=item["blocks"],
                bays=item["bays"],
                greedy=item["greedy_objective"],
                candidate=item["candidate_objective"],
                delta=item["objective_delta_vs_greedy"],
                match_or_better=item["matches_or_improves_greedy"],
                feasible=item["candidate_feasible"],
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These variants are deterministic stress checks created from public example data.",
            "They do not replace official training, preliminary, final, or leaderboard instances.",
            "The useful signal is regression safety: the single-file candidate remains official-checker feasible and is no worse than the public greedy reference on all included variants.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    zip_path = fetch_baseline_zip()
    with tempfile.TemporaryDirectory(prefix="ogc2026-robustness-") as tmp:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(tmp)
        base = Path(tmp) / "ogc2026"
        sys.path.insert(0, str(base / "baseline"))

        import baseline_greedy  # type: ignore
        from utils import check_feasibility  # type: ignore

        raw = json.loads((base / "alg_tester" / "example" / "example_B2_b10.json").read_text())
        module = load_myalgorithm()
        variants = []

        for block_count, bay_count in [(12, 2), (14, 3), (16, 3), (18, 3), (20, 3), (24, 3)]:
            instance = make_variant(raw, block_count=block_count, bay_count=bay_count)
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
                    f"candidate is worse than greedy on {instance['name']}: "
                    f"candidate={candidate_result['objective']} greedy={greedy_result['objective']}"
                )

            variants.append(
                {
                    "name": instance["name"],
                    "blocks": block_count,
                    "bays": bay_count,
                    "candidate_feasible": candidate_result["feasible"],
                    "candidate_stage": candidate_result["stage"],
                    "candidate_objective": candidate_result["objective"],
                    "candidate_obj1": candidate_result["obj1"],
                    "candidate_obj2": candidate_result["obj2"],
                    "candidate_obj3": candidate_result["obj3"],
                    "greedy_objective": greedy_result["objective"],
                    "greedy_obj1": greedy_result["obj1"],
                    "greedy_obj2": greedy_result["obj2"],
                    "greedy_obj3": greedy_result["obj3"],
                    "objective_delta_vs_greedy": round(delta, 6),
                    "objective_improvement": round(-delta, 6),
                    "matches_or_improves_greedy": delta <= 1e-6,
                }
            )

    payload = {
        "source": BASELINE_URL,
        "boundary": "deterministic public-example-derived robustness smoke only; not leaderboard evidence",
        "variant_count": len(variants),
        "all_candidates_feasible": all(item["candidate_feasible"] for item in variants),
        "all_candidates_improve_greedy": all(item["objective_improvement"] > 0 for item in variants),
        "all_candidates_match_or_improve_greedy": all(item["matches_or_improves_greedy"] for item in variants),
        "variants": variants,
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_report(payload)

    print("official_robustness_smoke_ok")
    print(f"variants={payload['variant_count']}")
    print(f"all_candidates_feasible={payload['all_candidates_feasible']}")
    print(f"all_candidates_improve_greedy={payload['all_candidates_improve_greedy']}")
    print(f"all_candidates_match_or_improve_greedy={payload['all_candidates_match_or_improve_greedy']}")
    for item in variants:
        print(
            f"{item['name']}: candidate={item['candidate_objective']:.6f} "
            f"greedy={item['greedy_objective']:.6f} delta={item['objective_delta_vs_greedy']:.6f}"
        )
    print(f"report={REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
