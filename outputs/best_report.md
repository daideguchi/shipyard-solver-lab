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

- Score: 1289.77
- Coverage: 1.0
- Yard utilization: 0.5177
- Packing compactness: 0.9048
- Placed blocks: 12
- Unplaced blocks: 0
- Weighted lateness: 0

## Placements

- `B09` -> `Y1` at (0, 0) size 14x14 rotated=False
- `B12` -> `Y1` at (14, 0) size 14x32 rotated=True
- `B05` -> `Y1` at (0, 14) size 14x24 rotated=True
- `B11` -> `Y1` at (28, 0) size 12x30 rotated=False
- `B01` -> `Y2` at (0, 0) size 12x28 rotated=True
- `B04` -> `Y2` at (12, 0) size 10x34 rotated=True
- `B07` -> `Y2` at (22, 0) size 18x30 rotated=True
- `B03` -> `Y2` at (22, 30) size 18x18 rotated=False
- `B08` -> `Y2` at (0, 34) size 22x12 rotated=False
- `B10` -> `Y3` at (0, 0) size 20x26 rotated=True
- `B06` -> `Y3` at (20, 0) size 16x22 rotated=False
- `B02` -> `Y3` at (36, 0) size 16x20 rotated=True

## Next Improvements

1. Add randomized multi-start construction.
2. Add relocate/swap/rotate local search.
3. Add official time/resource constraints when released.
4. Track every run by seed and keep the best solution archive.
