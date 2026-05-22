# Shipyard Solver Lab

Shipyard Solver Lab is a preparation workspace for Optimization Grand Challenge 2026.

The official challenge is "The Grand Shipyard Puzzle: Pack the Block, Beat the Clock." The goal is not a shiny demo app. The goal is a reproducible solver pipeline that can ingest official instances as soon as they are released, produce valid solutions, score them, and generate a technical report.

## Current Status

- Challenge: Optimization Grand Challenge 2026
- Official Devpost: https://ogc2026.devpost.com/
- Official site: https://www.optichallenge.com/
- Public repo: https://github.com/daideguchi/shipyard-solver-lab
- Public app: https://daideguchi.github.io/shipyard-solver-lab/
- Official problem statement and baseline package: publicly released on optichallenge.com
- Official training instances: not released yet
- Current solver: sample-instance beam search plus official-example projection smoke test plus a checker-validated official-format portfolio candidate

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
- Includes `official_submission/myalgorithm.py`, a candidate official algorithm wrapper.
- Runs an official-example portfolio smoke test that improves over the public greedy reference while staying checker-feasible.

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

The simple sequential solution is intentionally conservative and not competitive. Its purpose is to prove the exact official `operations` format and official feasibility checker integration. The next scoring step is to replace that safe placeholder with an optimized official-format algorithm while keeping the checker green.

## Official Portfolio Smoke Test

```bash
npm run official-portfolio
```

Current result:

```text
official_portfolio_smoke_ok
portfolio_feasible=True
portfolio_objective=1022.698826
greedy_objective=1055.727896
objective_improvement=33.029071
assignment_candidates=1024
portfolio_matches_static_bound=True
```

This uses the public OGC baseline example and the official feasibility checker. It is not leaderboard evidence, but it proves the repository now contains a checker-validated official-format algorithm candidate that improves over the public greedy reference on `example_B2_b10`. Because this public example has only 10 blocks and 2 bays, the smoke test also enumerates all 1,024 bay assignments and verifies that the candidate matches the static assignment lower bound for the example.

## What It Does Not Claim

- It does not solve the official OGC 2026 instance yet.
- It does not claim leaderboard performance.
- It does not use private or unreleased problem data.
- It does not claim eligibility or final submission readiness.
- The official-example projection does not claim official feasibility or official objective value.
- The official checker smoke proves format feasibility only; it does not claim competitive objective value.
- The official portfolio smoke is measured on the public example only; it is not a leaderboard or training-instance result.

## Run

```bash
python3 scripts/run_sample.py
python3 scripts/run_benchmark.py
python3 scripts/run_official_example_projection.py
npm run official-checker
npm run official-portfolio
python3 scripts/verify_solver.py
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
- `scripts/run_official_portfolio_smoke.py` — run official example through the candidate portfolio algorithm and checker
- `scripts/verify_solver.py` — regression check
- `official_submission/myalgorithm.py` — candidate official algorithm wrapper
- `outputs/sample_solution.json` — generated baseline output
- `outputs/best_solution.json` — current best sample output
- `outputs/benchmark.json` — candidate run archive with baseline-vs-best delta
- `outputs/sample_report.md` — generated technical report
- `outputs/best_report.md` — generated best-run report
- `outputs/official_example_projection_report.md` — public OGC example projection smoke-test report
- `outputs/official_checker_smoke_report.md` — official checker smoke-test report
- `outputs/official_portfolio_report.md` — official example portfolio improvement report
- `index.html` — lightweight dashboard

## Next Algorithm Steps

1. Match official input/output schema when published.
2. Add local search moves on top of the current beam output: relocate, swap, rotate, yard reassignment.
3. Add time-window and crane/resource constraints once official rules are known.
4. Add official benchmark runner with seed tracking and best-solution archive.
5. Generate final technical report from official runs only.
