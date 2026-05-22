# Shipyard Solver Lab — Sample Technical Report

This report is generated from a toy local instance. It is not an official OGC 2026 result.

## Instance

- Instance ID: `toy_shipyard_001`
- Yards: 3
- Blocks: 12

## Solver

- Solver: `beam_due_date_compact_y_w20`
- Seed: 7
- Order mode: `due_date`
- Placement mode: `compact_y`
- Beam width: 20
- Search: keeps the best partial layouts at each block step, using contact-point placements, rotation, yard reassignment, overlap checks, and compactness-aware ranking

## Metrics

- Score: 1297.33
- Coverage: 1.0
- Yard utilization: 0.5177
- Packing compactness: 0.9679
- Placed blocks: 12
- Unplaced blocks: 0
- Weighted lateness: 0

## Placements

- `B03` -> `Y1` at (0, 0) size 18x18 rotated=False
- `B09` -> `Y1` at (0, 18) size 14x14 rotated=False
- `B10` -> `Y1` at (18, 0) size 26x20 rotated=False
- `B11` -> `Y1` at (14, 20) size 30x12 rotated=True
- `B12` -> `Y1` at (44, 0) size 14x32 rotated=True
- `B01` -> `Y2` at (0, 0) size 28x12 rotated=False
- `B04` -> `Y2` at (0, 12) size 34x10 rotated=False
- `B06` -> `Y2` at (46, 0) size 16x22 rotated=False
- `B08` -> `Y2` at (34, 0) size 12x22 rotated=True
- `B02` -> `Y3` at (0, 0) size 20x16 rotated=False
- `B05` -> `Y3` at (0, 16) size 24x14 rotated=False
- `B07` -> `Y3` at (24, 0) size 18x30 rotated=True

## Next Improvements

1. Match the official OGC input/output schema as soon as problem files are released.
2. Add relocate, swap, rotate, and yard-reassignment local search on top of the beam output.
3. Add official time, resource, crane, and precedence constraints when released.
4. Track every run by seed, beam width, score, and validation errors.
