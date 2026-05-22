# Shipyard Solver Lab — Sample Technical Report

This report is generated from a toy local instance. It is not an official OGC 2026 result.

## Instance

- Instance ID: `toy_shipyard_001`
- Yards: 3
- Blocks: 12

## Solver

- Baseline: due-date-first first-fit placement
- Sort key: earliest due date, higher priority, larger area, earlier ready day
- Placement search: both orientations, all yards, low-top/low-right cost

## Metrics

- Score: 1274.36
- Coverage: 1.0
- Yard utilization: 0.5177
- Packing compactness: 0.7765
- Placed blocks: 12
- Unplaced blocks: 0
- Weighted lateness: 0

## Placements

- `B03` -> `Y1` at (0, 0) size 18x18 rotated=False
- `B04` -> `Y1` at (18, 0) size 34x10 rotated=False
- `B05` -> `Y1` at (52, 0) size 24x14 rotated=False
- `B07` -> `Y1` at (18, 10) size 30x18 rotated=False
- `B11` -> `Y1` at (48, 14) size 30x12 rotated=True
- `B01` -> `Y2` at (0, 0) size 28x12 rotated=False
- `B06` -> `Y2` at (28, 0) size 22x16 rotated=True
- `B09` -> `Y2` at (50, 0) size 14x14 rotated=False
- `B10` -> `Y2` at (0, 12) size 26x20 rotated=False
- `B02` -> `Y3` at (0, 0) size 20x16 rotated=False
- `B08` -> `Y3` at (20, 0) size 22x12 rotated=False
- `B12` -> `Y3` at (20, 12) size 32x14 rotated=False

## Next Improvements

1. Match the official OGC input/output schema as soon as problem files are released.
2. Add relocate, swap, rotate, and yard-reassignment local search on top of the beam output.
3. Add official time, resource, crane, and precedence constraints when released.
4. Track every run by seed, beam width, score, and validation errors.
