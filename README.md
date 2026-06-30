# Shipyard Solver Lab

Shipyard Solver Lab is a preparation workspace for Optimization Grand Challenge 2026.

The official challenge is "The Grand Shipyard Puzzle: Pack the Block, Beat the Clock." The goal is not a shiny demo app. The goal is a reproducible solver pipeline that can ingest official instances as soon as they are released, produce valid solutions, score them, and generate a technical report.

## Current Status

- Challenge: Optimization Grand Challenge 2026
- Official Devpost: https://ogc2026.devpost.com/
- Official site: https://www.optichallenge.com/
- Public repo: https://github.com/daideguchi/shipyard-solver-lab
- Public app: https://daideguchi.github.io/shipyard-solver-lab/
- Japanese README: [README.ja.md](README.ja.md)
- Narrated demo video: `media/shipyard-solver-lab-demo-narrated.mp4`
- Demo thumbnail: `media/shipyard-solver-lab-demo-thumb.png`
- Official problem statement and baseline package: publicly released on optichallenge.com
- Official training instances: not released yet
- Current solver: sample-instance beam search plus official-example projection smoke test plus a standalone import-free official-format candidate and deterministic robustness smoke variants

## Judge Quick Read

One-sentence pitch:

```text
For optimization competitors who need proof before official data opens, Shipyard Solver Lab turns the shipyard puzzle into a reproducible solve-validate-package loop.
```

Who it helps:

```text
Contest builders who need a solver, checker, benchmark, report, and submission package to move together.
```

Problem:

```text
An optimization idea is not enough. If the checker fails, the benchmark is not reproducible, or the package shape is wrong, the entry loses trust before scoring begins.
```

How it solves the problem:

```text
The repo connects solver output, official-example ingestion, official checker smoke tests, a single-file official candidate, robustness reports, screenshots, narrated demo assets, and a candidate submission zip.
```

Judge signal:

```text
This is not a decorative dashboard. It is an operating loop that proves the team can iterate quickly and keep the official checker green.
```

## 30-Second Review Path

1. Read the one-sentence pitch to understand the solve-validate-package loop.
2. Open the live app and scan the top proof cards.
3. Check the official checker, official candidate, robustness, and package proof cards.
4. Confirm the boundary: this is readiness proof on sample and public example data, not a final leaderboard claim.

## Why This Exists

Optimization contests are won by iteration speed:

1. load the instance
2. produce a valid baseline
3. score it locally
4. inspect what failed
5. improve the algorithm
6. document the method

This repository builds that loop before the official data arrives.

## What It Does Now

- Loads a toy shipyard block-packing instance.
- Places rectangular blocks into rectangular yards.
- Checks boundary and overlap validity.
- Scores utilization, lateness, and unplaced blocks.
- Writes a solution JSON.
- Writes a technical report draft.
- Runs a 1,051-candidate benchmark archive.
- Keeps the best solution JSON.
- Serves a static dashboard that visualizes the latest sample output.
- Shows a scored improvement trail over the baseline.
- Downloads the public OGC baseline package and ingests `example_B2_b10.json` as a projection smoke test.
- Projects official polygon/layer blocks into rectangles for early schema-readiness testing.
- Runs the public official feasibility checker through a conservative official-format smoke solution.
- Includes `official_submission/myalgorithm.py`, a standalone import-free candidate official algorithm.
- Runs an official-example portfolio smoke test that stays checker-feasible and no worse than the public greedy reference.
- Runs deterministic public-example-derived robustness smoke tests that keep the candidate checker-feasible and no worse than greedy on six expanded variants.
- Builds an official-platform candidate zip containing `myalgorithm.py`.

## Current Sample Result

```text
best solver: beam_due_date_compact_y_w20
best score: 1297.33
baseline score: 1274.36
delta: +22.97
valid candidates: 1051 / 1051
placed blocks: 12 / 12
```

## Official Example Projection Smoke Test

```bash
python3 scripts/run_official_example_projection.py
```

Current result:

```text
official_name=example_B2_b10
projected_blocks=10
baseline_score=1195.74
beam_score=1204.76
delta=+9.02
```

This is not official scoring. It is an ingestion-readiness test against the public OGC baseline example. See [Official OGC Readiness Notes](docs/OFFICIAL_READINESS.md).

## Official Checker Smoke Test

```bash
npm run official-checker
```

Current result:

```text
official_checker_smoke_ok
simple_feasible=True
simple_objective=281320.786203
greedy_feasible=True
greedy_objective=1055.727896
```

The simple sequential solution is intentionally conservative and not competitive. Its purpose is to prove the exact official `operations` format and official feasibility checker integration. The current submission candidate below is the path intended for official zip packaging.

## Official Portfolio Smoke Test

```bash
npm run official-portfolio
```

Current result:

```text
official_portfolio_smoke_ok
portfolio_feasible=True
portfolio_objective=1055.727896
greedy_objective=1055.727896
objective_delta_vs_greedy=0.000000
matches_or_improves_greedy=True
```

This uses the public OGC baseline example and the official feasibility checker. It is not leaderboard evidence, but it proves the repository now contains a checker-validated official-format algorithm candidate that is no worse than the public greedy reference on `example_B2_b10`.

The candidate is intentionally standalone: the official platform extracts only `myalgorithm.py`, so the solver avoids repo-local imports. It builds conservative bounding-box placements, handles reference-offset coordinates, skips unsafe orientations, tries several deterministic block orders, and keeps the best official-format solution it can construct.

## Official Robustness Smoke Test

```bash
npm run official-robustness
```

Current result:

```text
official_robustness_smoke_ok
variants=6
all_candidates_feasible=True
all_candidates_improve_greedy=True
synthetic_B2_b12: candidate=1512.370044 greedy=1812.553857 delta_vs_greedy=-300.183813
synthetic_B3_b14: candidate=1107.497693 greedy=2611.626011 delta_vs_greedy=-1504.128318
synthetic_B3_b16: candidate=1360.556393 greedy=1748.195903 delta_vs_greedy=-387.639509
synthetic_B3_b18: candidate=1183.073511 greedy=3744.245261 delta_vs_greedy=-2561.171751
synthetic_B3_b20: candidate=1532.799001 greedy=4472.911928 delta_vs_greedy=-2940.112927
synthetic_B3_b24: candidate=2215.626445 greedy=2847.708322 delta_vs_greedy=-632.081876
```

This is a deterministic stress check built from the public OGC example. It is not official leaderboard evidence and it does not replace official training or final instances. Its value is regression safety: the single-file candidate stays official-checker feasible and is no worse than the public greedy reference on six larger public-example-derived variants.

For a broader regression probe:

```bash
npm run official-deep-robustness
```

Current result:

```text
official_deep_robustness_probe_ok
variants=40
all_candidates_feasible=True
all_candidates_match_or_improve_greedy=True
improved_count=38
worst_delta_vs_greedy=0.000000
best_improvement_vs_greedy=4052.616781
```

This uses only public-example-derived variants. It is still not leaderboard evidence, but it gives a wider no-worse regression check before sending another official package.

## Official Submission Package

```bash
npm run official-package
```

Current output:

```text
outputs/official_submission_candidate.zip
outputs/official_submission_manifest.json
```

The zip contains `myalgorithm.py` at the archive root, matching the public organizer template shape. The current candidate package is a readiness artifact until it is sent through the official OGC email/platform window.

## Demo Assets

The repository includes a short narrated demo for judges and reviewers:

- `media/shipyard-solver-lab-demo-narrated.mp4` - 118 second narrated walkthrough with video, audio, and subtitle streams
- `media/shipyard-solver-lab-demo-thumb.png` - thumbnail captured from the latest dashboard
- `media/shipyard-solver-lab-full.png` - full-page verification screenshot generated by `npm run verify`

The demo shows the dashboard, official-example projection, official checker smoke, official candidate, official package proof, yard layout, and solution table. It is a product walkthrough, not leaderboard evidence.

To rebuild the demo locally:

```bash
npm run demo:narrated
```

## What It Does Not Claim

- It does not solve the official OGC 2026 instance yet.
- It does not claim leaderboard performance.
- It does not use private or unreleased problem data.
- It does not claim eligibility or final leaderboard performance.
- The official-example projection does not claim official feasibility or official objective value.
- The official checker smoke proves format feasibility only; it does not claim competitive objective value.
- The official portfolio smoke is measured on the public example only; it is not a leaderboard or training-instance result.
- The official robustness smoke uses deterministic variants derived from the public example only; it is not official training, preliminary, final, or leaderboard evidence.
- The official submission zip is a candidate package only; it must be sent only through an allowed official OGC submission window.

## Run

```bash
python3 scripts/run_sample.py
python3 scripts/run_benchmark.py
python3 scripts/run_official_example_projection.py
npm run official-checker
npm run official-portfolio
npm run official-robustness
npm run official-package
npm run demo:narrated
python3 scripts/verify_solver.py
npm run verify
```

Open the dashboard:

```bash
open index.html
```

## Files

- `data/sample_blocks.json` — small local toy instance
- `shipyard_solver/solver.py` — baseline placement algorithm
- `shipyard_solver/scoring.py` — validity and score logic
- `scripts/run_sample.py` — generate solution and report
- `scripts/run_benchmark.py` — run multi-start solver candidates
- `scripts/run_official_example_projection.py` — download public OGC baseline example and run schema projection smoke test
- `scripts/run_official_checker_smoke.py` — run official-format smoke solution and official checker via `uv`
- `scripts/run_official_portfolio_smoke.py` — run official example through the single-file candidate algorithm and checker
- `scripts/run_official_robustness_smoke.py` — run deterministic public-example-derived variants through the candidate algorithm and official checker
- `scripts/build_official_submission_package.py` — package `official_submission/myalgorithm.py` as a candidate official zip
- `scripts/record_demo.mjs` — record the browser walkthrough video
- `scripts/build_narrated_demo.sh` — build the narrated MP4 and thumbnail
- `scripts/verify_demo_assets.py` — verify that the demo video has video, audio, and subtitles
- `scripts/verify_solver.py` — regression check
- `official_submission/myalgorithm.py` — standalone import-free candidate official algorithm
- `outputs/sample_solution.json` — generated baseline output
- `outputs/best_solution.json` — current best sample output
- `outputs/benchmark.json` — candidate run archive with baseline-vs-best delta
- `outputs/sample_report.md` — generated technical report
- `outputs/best_report.md` — generated best-run report
- `outputs/official_example_projection_report.md` — public OGC example projection smoke-test report
- `outputs/official_checker_smoke_report.md` — official checker smoke-test report
- `outputs/official_portfolio_report.md` — official example candidate feasibility report
- `outputs/official_robustness_report.md` — deterministic robustness smoke-test report
- `outputs/official_robustness_result.json` — machine-readable robustness smoke-test result
- `outputs/official_submission_candidate.zip` — candidate package for official platform readiness
- `outputs/official_submission_manifest.json` — package hash and file manifest
- `media/shipyard-solver-lab-demo-narrated.mp4` — narrated demo video
- `media/shipyard-solver-lab-demo-thumb.png` — demo thumbnail
- `index.html` — lightweight dashboard

## Next Algorithm Steps

1. Keep the standalone `myalgorithm.py` package self-contained and checker-feasible.
2. Improve objective quality against official training and preliminary instances as soon as they are available.
3. Add deeper placement-level search inside the import-free official candidate without depending on repo-local helper modules.
4. Add official benchmark runner with seed tracking and best-solution archive.
5. Generate final technical report from official runs only.
