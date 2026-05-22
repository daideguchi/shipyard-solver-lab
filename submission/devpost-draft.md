# Devpost Draft — Shipyard Solver Lab

Live app: https://daideguchi.github.io/shipyard-solver-lab/

Source code: https://github.com/daideguchi/shipyard-solver-lab

## Inspiration

Optimization challenges are not won by a beautiful UI. They are won by a fast, honest loop: load the instance, generate a valid solution, score it, inspect what failed, improve the algorithm, and document the method.

Shipyard Solver Lab is my preparation workbench for Optimization Grand Challenge 2026. The official problem is about packing and scheduling shipyard blocks under constraints. Before the official data is released, I built the repeatable pipeline I will need once the real competition begins.

## What It Does

The current version runs on a toy local instance and demonstrates the full loop:

- load shipyard yards and blocks
- build a baseline placement solution
- run beam search candidates
- validate boundaries and overlaps
- score coverage, utilization, lateness, and unplaced blocks
- generate a solution JSON
- generate a technical report draft
- run a 1,051-candidate benchmark archive
- keep the best sample solution
- show the score improvement over the baseline
- visualize the solution in a browser dashboard

## How I Built It

The solver is written in Python. It now includes a baseline, multi-start constructive search, and a beam search that keeps multiple partial layouts at each block step. It uses contact-point placements, rotation, yard reassignment, boundary checks, overlap validation, and compactness-aware ranking.

On the current toy instance, the benchmark validates 1,051 candidates. The best beam-search run scores 1297.33, compared with the baseline score of 1274.36, a +22.97 point improvement. The dashboard is a static HTML/JavaScript visualizer that reads the generated best-solution JSON and benchmark archive.

The current solver intentionally stays schema-flexible because official OGC data is not attached here yet. The value is the structure: when official input/output schemas are available, the loader, scorer, benchmark runner, and report generator can be adapted quickly.

After checking the official OGC site, I added a schema-ingestion smoke test against the public baseline package. The script downloads the official baseline zip, reads `example_B2_b10.json`, projects polygon/layer block geometry into this lab's rectangle model, and runs the beam solver. On that projection, the beam run scores 1204.76 versus a baseline projection score of 1195.74, a +9.02 point delta. This is not official scoring; it is a readiness proof that the pipeline can read the official-style example and produce a validated internal projection.

## Claim Boundary

This is a preparation workbench. It does not claim official OGC 2026 leaderboard performance, official feasibility, official objective value, or final submission readiness.

## What's Next

- adapt to the official schema
- add relocate/swap/rotate local search on top of beam output
- add resource and time-window constraints once official rules are published
- archive best runs by seed and score
- write the final technical report from real benchmark evidence
