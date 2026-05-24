# Submission Package — Shipyard Solver Lab

## Project Name

Shipyard Solver Lab

## Tagline

Reproducible optimization workbench for packing shipyard blocks.

## One-Sentence Pitch

For optimization competitors who need proof before official data opens, Shipyard Solver Lab turns the shipyard puzzle into a reproducible solve-validate-package loop.

## Who / Problem / How

- Who: OGC builders who need solver progress, checker proof, benchmarks, reports, and package readiness in one loop.
- Problem: an algorithm idea is not enough if the checker fails, outputs are not reproducible, or the submission package is shaped wrong.
- How: the repo runs solver benchmarks, official-example projection, official checker smoke, public-example portfolio search, deterministic robustness smoke variants, generated reports, screenshots, narrated demo assets, and a candidate official zip.

## Public Links

- Live app: https://daideguchi.github.io/shipyard-solver-lab/
- GitHub repo: https://github.com/daideguchi/shipyard-solver-lab
- Best report: `outputs/best_report.md`
- Benchmark archive: `outputs/benchmark.json`
- Official readiness notes: `docs/OFFICIAL_READINESS.md`
- Official example projection report: `outputs/official_example_projection_report.md`
- Official checker smoke report: `outputs/official_checker_smoke_report.md`
- Official portfolio smoke report: `outputs/official_portfolio_report.md`
- Candidate official package: `outputs/official_submission_candidate.zip`
- Candidate package manifest: `outputs/official_submission_manifest.json`
- Screenshot: `media/shipyard-solver-lab-full.png`
- Narrated demo video: `media/shipyard-solver-lab-demo-narrated.mp4`
- Demo thumbnail: `media/shipyard-solver-lab-demo-thumb.png`

## 250-500 Word Project Description

Shipyard Solver Lab is a preparation workbench for Optimization Grand Challenge 2026 and the Grand Shipyard Puzzle.

The project is built around a practical contest reality: optimization challenges are not won by a pretty UI alone. They are won by a repeatable loop: load the instance, generate a valid solution, score it locally, inspect what failed, improve the algorithm, and document the method clearly enough that another person can reproduce it.

The current public build runs on a toy shipyard-style instance because the official problem files are not included in this repository yet. That boundary is intentional and explicit. The goal of this build is to prove the solver pipeline before the official data arrives.

The solver is written in Python. It includes a baseline, multi-start constructive search, and a beam search that keeps multiple partial layouts at each block step. Candidate placements use contact points, rotation, yard reassignment, boundary checks, overlap validation, and compactness-aware ranking. On the current sample instance, the benchmark validates 1,051 candidates. The best beam-search run scores 1297.33, compared with a baseline score of 1274.36, a +22.97 point improvement.

After checking the official OGC site, I also added an official-example projection smoke test. The script downloads the public OGC baseline package, reads `example_B2_b10.json`, projects polygon/layer blocks into this lab's rectangle model, and runs the beam solver. The current projection places 10 projected blocks, scores 1204.76 versus a baseline projection score of 1195.74, and records a +9.02 projection delta. This is not official scoring; it proves schema-ingestion readiness while preserving the claim boundary.

I also added an exact official-checker smoke test. It builds a conservative official `operations` solution, runs the public OGC feasibility checker, and verifies `feasible=True` at stage 5. The objective is intentionally poor because only one block is present at a time. That is a feature, not a claim: it proves the submission format and checker integration before optimizing.

The latest step replaces that placeholder with a real candidate official algorithm in `official_submission/myalgorithm.py`. It runs the public greedy baseline, then searches bay-assignment candidates and keeps the best official-checker-feasible solution. On the public `example_B2_b10` instance, the candidate improves the official checker objective from 1055.73 to 1022.70, a 33.03 point improvement over the public greedy reference. Because the public example has only 10 blocks and 2 bays, the smoke test enumerates all 1,024 bay assignments and verifies that the candidate matches the static assignment lower bound. This is not leaderboard evidence, but it is no longer just a format smoke test: it is a working, checker-validated optimization loop on the public example.

To reduce the risk of overfitting the tiny public example, I added a deterministic robustness smoke test. It creates three larger variants from the public example, then compares the candidate algorithm with the public greedy reference through the official feasibility checker. The candidate stays feasible and improves greedy on all three variants: +446.50 on `synthetic_B2_b12`, +1526.81 on `synthetic_B3_b14`, and +846.29 on `synthetic_B3_b16`. These are still public-example-derived checks, not leaderboard evidence. The value is practical: the repository now has a regression guard for larger official-format inputs before official training instances are available.

The repository also builds `outputs/official_submission_candidate.zip`, a candidate package with `myalgorithm.py` at the archive root. This is not submitted yet; it is a readiness artifact for when the official platform opens.

The browser dashboard reads generated JSON artifacts and visualizes the best solution. It also displays the run boundary, benchmark count, baseline improvement, best solver name, and placement table. The generated technical report records the instance, solver parameters, metrics, placements, and next algorithm steps. For review, the repository includes a 118 second narrated demo video with video, audio, and subtitle streams. The demo walks through the dashboard, official-example projection, official checker smoke, official portfolio candidate, official package proof, yard layout, and solution table. It is a walkthrough of the reproducible workflow, not leaderboard evidence.

This is not claiming official OGC leaderboard performance. It is a contest-ready operating loop: solver, validator, scorer, benchmark archive, dashboard, and report generator. When the official schema and data are available, this repository is ready to swap in the official loader and continue improving the algorithm from a reproducible baseline.

## Claim Boundary

- This repository does not include or claim official OGC 2026 data.
- It does not claim leaderboard performance.
- It does not claim final submission readiness.
- The dashboard currently shows a local toy instance used to prove the workflow.
- The official-example projection is not official feasibility or official objective scoring.
- The official checker smoke proves format feasibility only; it is not competitive.
- The official portfolio smoke is measured only on the public example, not on official training, preliminary, final, or leaderboard instances.
- The official robustness smoke uses deterministic variants derived from the public example only; it is not official training, preliminary, final, or leaderboard evidence.
- The official submission zip is a candidate package only and has not been uploaded to the official OGC platform.
- The narrated demo is a product walkthrough only; it does not add any leaderboard claim.

## Verification

```bash
npm run verify
```

Expected markers:

```text
official_example_projection_ok
official_checker_smoke_ok
official_portfolio_smoke_ok
official_robustness_smoke_ok
official_submission_package_ok
shipyard_solver_verify_ok
shipyard_solver_no_secrets_ok
shipyard_solver_app_verify_ok
shipyard_solver_demo_assets_ok
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

Official portfolio smoke:

```bash
npm run official-portfolio
official_portfolio_smoke_ok
portfolio_feasible=True
portfolio_objective=1022.698826
greedy_objective=1055.727896
objective_improvement=33.029071
assignment_candidates=1024
portfolio_matches_static_bound=True
```

Official robustness smoke:

```bash
npm run official-robustness
official_robustness_smoke_ok
variants=3
all_candidates_feasible=True
all_candidates_improve_greedy=True
synthetic_B2_b12: candidate=1366.056678 greedy=1812.553857 improvement=446.497179
synthetic_B3_b14: candidate=1084.812759 greedy=2611.626011 improvement=1526.813252
synthetic_B3_b16: candidate=901.905038 greedy=1748.195903 improvement=846.290865
```

Official package:

```bash
npm run official-package
official_submission_package_ok
zip=outputs/official_submission_candidate.zip
manifest=outputs/official_submission_manifest.json
```

Demo video:

```bash
npm run demo:narrated
python3 scripts/verify_demo_assets.py
shipyard_solver_demo_assets_ok
duration=118.48
streams=audio,subtitle,video
```
