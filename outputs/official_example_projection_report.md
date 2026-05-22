# Official OGC Example Projection Smoke Test

This report uses the public OGC 2026 baseline package example instance.
It projects official polygon/layer block data into this lab's rectangle model.
That proves schema ingestion, but it is not official OGC feasibility or leaderboard scoring.

## Projection Boundary

- Official OGC polygon/layer data projected to rectangles for schema-ingestion smoke testing only; not official feasibility or leaderboard scoring.
- Projected bays: 2
- Projected blocks: 10
- Baseline projection score: 1195.74
- Beam projection score: 1204.76
- Projection delta: 9.02

## Generated Lab Report
# Shipyard Solver Lab — Sample Technical Report

Official OGC polygon/layer data projected to rectangles for schema-ingestion smoke testing only; not official feasibility or leaderboard scoring.

## Instance

- Instance ID: `example_B2_b10`
- Yards: 2
- Blocks: 10

## Solver

- Solver: `beam_area_first_compact_y_w80`
- Seed: 0
- Order mode: `area_first`
- Placement mode: `compact_y`
- Beam width: 80
- Search: keeps the best partial layouts at each block step, using contact-point placements, rotation, yard reassignment, overlap checks, and compactness-aware ranking

## Metrics

- Score: 1204.76
- Coverage: 1.0
- Yard utilization: 0.256
- Packing compactness: 0.9598
- Placed blocks: 10
- Unplaced blocks: 0
- Weighted lateness: 0

## Placements

- `block_1` -> `bay_0` at (0, 0) size 12x10 rotated=False
- `block_4` -> `bay_0` at (40, 1) size 6x9 rotated=False
- `block_5` -> `bay_0` at (12, 0) size 11x10 rotated=True
- `block_7` -> `bay_0` at (32, 1) size 8x9 rotated=False
- `block_8` -> `bay_0` at (46, 1) size 6x9 rotated=True
- `block_9` -> `bay_0` at (23, 0) size 9x10 rotated=False
- `block_0` -> `bay_1` at (31, 1) size 15x6 rotated=False
- `block_2` -> `bay_1` at (46, 0) size 4x7 rotated=False
- `block_3` -> `bay_1` at (0, 0) size 18x7 rotated=False
- `block_6` -> `bay_1` at (18, 0) size 13x7 rotated=False

## Next Improvements

1. Match the official OGC input/output schema as soon as problem files are released.
2. Add relocate, swap, rotate, and yard-reassignment local search on top of the beam output.
3. Add official time, resource, crane, and precedence constraints when released.
4. Track every run by seed, beam width, score, and validation errors.
