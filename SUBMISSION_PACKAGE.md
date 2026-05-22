# Submission Package — Shipyard Solver Lab

## Project Name

Shipyard Solver Lab

## Tagline

Reproducible optimization workbench for packing shipyard blocks.

## Public Links

- Live app: https://daideguchi.github.io/shipyard-solver-lab/
- GitHub repo: https://github.com/daideguchi/shipyard-solver-lab
- Best report: `outputs/best_report.md`
- Benchmark archive: `outputs/benchmark.json`
- Official readiness notes: `docs/OFFICIAL_READINESS.md`
- Official example projection report: `outputs/official_example_projection_report.md`
- Official checker smoke report: `outputs/official_checker_smoke_report.md`
- Screenshot: `media/shipyard-solver-lab-full.png`

## 250-500 Word Project Description

Shipyard Solver Lab is a preparation workbench for Optimization Grand Challenge 2026 and the Grand Shipyard Puzzle.

The project is built around a practical contest reality: optimization challenges are not won by a pretty UI alone. They are won by a repeatable loop: load the instance, generate a valid solution, score it locally, inspect what failed, improve the algorithm, and document the method clearly enough that another person can reproduce it.

The current public build runs on a toy shipyard-style instance because the official problem files are not included in this repository yet. That boundary is intentional and explicit. The goal of this build is to prove the solver pipeline before the official data arrives.

The solver is written in Python. It includes a baseline, multi-start constructive search, and a beam search that keeps multiple partial layouts at each block step. Candidate placements use contact points, rotation, yard reassignment, boundary checks, overlap validation, and compactness-aware ranking. On the current sample instance, the benchmark validates 1,051 candidates. The best beam-search run scores 1297.33, compared with a baseline score of 1274.36, a +22.97 point improvement.

After checking the official OGC site, I also added an official-example projection smoke test. The script downloads the public OGC baseline package, reads `example_B2_b10.json`, projects polygon/layer blocks into this lab's rectangle model, and runs the beam solver. The current projection places 10 projected blocks, scores 1204.76 versus a baseline projection score of 1195.74, and records a +9.02 projection delta. This is not official scoring; it proves schema-ingestion readiness while preserving the claim boundary.

I also added an exact official-checker smoke test. It builds a conservative official `operations` solution, runs the public OGC feasibility checker, and verifies `feasible=True` at stage 5. The objective is intentionally poor because only one block is present at a time. That is a feature, not a claim: it proves the submission format and checker integration before optimizing.

The browser dashboard reads generated JSON artifacts and visualizes the best solution. It also displays the run boundary, benchmark count, baseline improvement, best solver name, and placement table. The generated technical report records the instance, solver parameters, metrics, placements, and next algorithm steps.

This is not claiming official OGC leaderboard performance. It is a contest-ready operating loop: solver, validator, scorer, benchmark archive, dashboard, and report generator. When the official schema and data are available, this repository is ready to swap in the official loader and continue improving the algorithm from a reproducible baseline.

## Claim Boundary

- This repository does not include or claim official OGC 2026 data.
- It does not claim leaderboard performance.
- It does not claim final submission readiness.
- The dashboard currently shows a local toy instance used to prove the workflow.
- The official-example projection is not official feasibility or official objective scoring.
- The official checker smoke proves format feasibility only; it is not competitive.

## Verification

```bash
npm run verify
```

Expected markers:

```text
shipyard_solver_verify_ok
shipyard_solver_no_secrets_ok
shipyard_solver_app_verify_ok
```

Official projection smoke test:

```bash
python3 scripts/run_official_example_projection.py
official_example_projection_ok
projected_blocks=10
beam_score=1204.76
delta=9.02
```

Official checker smoke:

```bash
npm run official-checker
official_checker_smoke_ok
simple_feasible=True
greedy_feasible=True
```
