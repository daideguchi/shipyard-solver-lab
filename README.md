# Shipyard Solver Lab

Shipyard Solver Lab is a preparation workspace for Optimization Grand Challenge 2026.

The official challenge is "The Grand Shipyard Puzzle: Pack the Block, Beat the Clock." The goal is not a shiny demo app. The goal is a reproducible solver pipeline that can ingest official instances as soon as they are released, produce valid solutions, score them, and generate a technical report.

## Current Status

- Challenge: Optimization Grand Challenge 2026
- Official Devpost: https://ogc2026.devpost.com/
- Official site: https://www.optichallenge.com/
- Public repo: pending
- Public app: pending
- Official problem files: not attached in this repository yet
- Current solver: sample-instance baseline only

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
- Serves a static dashboard that visualizes the latest sample output.

## What It Does Not Claim

- It does not solve the official OGC 2026 instance yet.
- It does not claim leaderboard performance.
- It does not use private or unreleased problem data.
- It does not claim eligibility or final submission readiness.

## Run

```bash
python3 scripts/run_sample.py
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
- `scripts/verify_solver.py` — regression check
- `outputs/sample_solution.json` — generated baseline output
- `outputs/sample_report.md` — generated technical report
- `index.html` — lightweight dashboard

## Next Algorithm Steps

1. Match official input/output schema when published.
2. Add multi-start randomized constructive heuristics.
3. Add local search moves: relocate, swap, rotate, yard reassignment.
4. Add time-window and crane/resource constraints once official rules are known.
5. Add benchmark runner with seed tracking and best-solution archive.

