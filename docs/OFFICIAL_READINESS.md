# Official OGC Readiness Notes

Source checked: https://www.optichallenge.com/problem-description

## Current Official State

- Problem Statement v1.0 is released.
- Baseline Algorithm & Development Environment v1.0 is released.
- Training Problem Instances are still marked `COMING SOON`.
- Registration opens on May 25, 2026 at 00:00 KST.
- Devpost submission period opens on May 25, 2026 at 09:00 KST.

## Official Baseline Interface

The public baseline package expects an algorithm folder containing:

```python
def algorithm(prob_info: dict, timelimit: float) -> dict:
    ...
    return solution
```

The official package includes:

- `baseline/myalgorithm.py`
- `baseline/baseline_greedy.py`
- `baseline/utils.py`
- `alg_tester/example/example_B2_b10.json`
- `alg_tester/alg_tester_app.py`

The official feasibility checker remains the source of truth for official scoring.

## What This Repository Added

This repository now includes a schema-ingestion smoke test:

```bash
python3 scripts/run_official_example_projection.py
```

It downloads the public baseline package, reads `example_B2_b10.json`, projects polygon/layer block data into this lab's rectangle model, runs the beam solver, and writes:

```text
outputs/official_example_projection_instance.json
outputs/official_example_projection_solution.json
outputs/official_example_projection_report.md
```

Current projection result:

```text
projected_blocks=10
baseline_score=1195.74
beam_score=1204.76
delta=+9.02
```

It also includes an exact official-checker smoke test:

```bash
npm run official-checker
```

This creates a conservative official `operations` solution and checks it with the public OGC baseline package:

```text
simple_feasible=True
simple_objective=281320.786203
greedy_feasible=True
greedy_objective=1055.727896
```

The simple sequential solution is deliberately not competitive. It proves format and checker integration only.

## Boundary

This projection is not an official OGC solver result. It proves that the lab can ingest the official example schema and run the existing search pipeline over a simplified rectangle projection.

Still required for real competition work:

1. Implement the exact official solution format.
2. Run the official `utils.check_feasibility`.
3. Model polygon/layer collisions and crane entry/exit constraints directly.
4. Use official training/preliminary instances when released.
5. Submit through the official OGC platform, not only Devpost.
