# Shipyard Solver Lab

Shipyard Solver Lab is a preparation workspace for Optimization Grand Challenge 2026.

The official challenge is "The Grand Shipyard Puzzle: Pack the Block, Beat the Clock." The goal is not a shiny demo app. The goal is a reproducible solver pipeline that can ingest official instances as soon as they are released, produce valid solutions, score them, and generate a technical report.

## Current Status

- Challenge: Optimization Grand Challenge 2026
- Official Devpost: https://ogc2026.devpost.com/
- Official site: https://www.optichallenge.com/
- Public repo: https://github.com/daideguchi/shipyard-solver-lab
- Public app: https://daideguchi.github.io/shipyard-solver-lab/
- Official problem files: not attached in this repository yet
- Current solver: sample-instance beam search plus multi-start constructive baselines

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
- Runs a 451-candidate benchmark archive.
- Keeps the best solution JSON.
- Serves a static dashboard that visualizes the latest sample output.
- Runs a 1,051-candidate benchmark archive after adding beam search.
- Shows a scored improvement trail over the baseline.

## Current Sample Result

```text
best solver: beam_due_date_compact_y_w20
best score: 1297.33
baseline score: 1274.36
delta: +22.97
valid candidates: 1051 / 1051
placed blocks: 12 / 12
```

## What It Does Not Claim

- It does not solve the official OGC 2026 instance yet.
- It does not claim leaderboard performance.
- It does not use private or unreleased problem data.
- It does not claim eligibility or final submission readiness.

## Run

```bash
python3 scripts/run_sample.py
python3 scripts/run_benchmark.py
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
- `scripts/verify_solver.py` — regression check
- `outputs/sample_solution.json` — generated baseline output
- `outputs/best_solution.json` — current best sample output
- `outputs/benchmark.json` — candidate run archive with baseline-vs-best delta
- `outputs/sample_report.md` — generated technical report
- `outputs/best_report.md` — generated best-run report
- `index.html` — lightweight dashboard

## Next Algorithm Steps

1. Match official input/output schema when published.
2. Add local search moves on top of the current beam output: relocate, swap, rotate, yard reassignment.
3. Add time-window and crane/resource constraints once official rules are known.
4. Add official benchmark runner with seed tracking and best-solution archive.
5. Generate final technical report from official runs only.
