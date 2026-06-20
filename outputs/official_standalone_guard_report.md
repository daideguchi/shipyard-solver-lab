# Official Standalone Guard Smoke Report

This report targets hidden-instance risk in the single-file fallback algorithm.

## Guards

- `example_B2_b10`: feasible=True stage=5 entry={'type': 'ENTRY', 'block_id': 1, 'bay_id': 0, 'x': 0, 'y': 8, 'orient_idx': 0}
- `standalone_fractional_time_guard`: feasible=True stage=5 entry={'type': 'ENTRY', 'block_id': 0, 'bay_id': 0, 'x': 0, 'y': 0, 'orient_idx': 0}
- `standalone_integer_position_guard`: feasible=True stage=5 entry={'type': 'ENTRY', 'block_id': 0, 'bay_id': 0, 'x': 0, 'y': 0, 'orient_idx': 1}
- `standalone_reference_offset_guard`: feasible=True stage=5 entry={'type': 'ENTRY', 'block_id': 0, 'bay_id': 0, 'x': 0, 'y': 0, 'orient_idx': 0}
- `standalone_cancellation_bound_guard`: feasible=True stage=5 entry={'type': 'ENTRY', 'block_id': 0, 'bay_id': 0, 'x': 0, 'y': 0, 'orient_idx': 1}

## Boundary

These are small synthetic guard cases. They do not claim leaderboard quality.
They verify that the submitted single-file algorithm handles fractional timing and skips an orientation that cannot be placed at any integer coordinate inside the bay.
