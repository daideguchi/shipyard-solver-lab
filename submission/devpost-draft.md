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
- validate boundaries and overlaps
- score coverage, utilization, lateness, and unplaced blocks
- generate a solution JSON
- generate a technical report draft
- run a multi-start benchmark archive
- keep the best sample solution
- visualize the solution in a browser dashboard

## How I Built It

The solver is written in Python. It now includes a baseline plus multi-start constructive search across ordering and placement strategies. The dashboard is a static HTML/JavaScript visualizer that reads the generated best-solution JSON and benchmark archive.

The current solver intentionally stays schema-flexible because official OGC data is not attached here yet. The value is the structure: when official input/output schemas are available, the loader, scorer, benchmark runner, and report generator can be adapted quickly.

## Claim Boundary

This is a preparation workbench. It does not claim official OGC 2026 leaderboard performance, official data access, or final submission readiness.

## What's Next

- adapt to the official schema
- add randomized multi-start construction
- add relocate/swap/rotate local search
- add resource and time-window constraints once official rules are published
- archive best runs by seed and score
- write the final technical report from real benchmark evidence
