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

It now also includes a checker-validated candidate official algorithm:

```bash
npm run official-portfolio
```

The candidate lives at:

```text
official_submission/myalgorithm.py
```

It is a standalone import-free official-format solver because the official platform extracts only `myalgorithm.py`. It builds conservative bounding-box placements, handles reference-offset coordinates, skips unsafe orientations, tries several deterministic block orders, and returns the best checker-feasible official-format solution it can construct.

Current public example result:

```text
portfolio_feasible=True
portfolio_objective=1055.727896
greedy_objective=1055.727896
objective_delta_vs_greedy=0.000000
matches_or_improves_greedy=True
```

This is measured only on the public `example_B2_b10` example. It is not leaderboard evidence, but it proves the exact official algorithm interface, `operations` format, checker integration, and a submission-safe single-file candidate that is no worse than the public greedy reference on the available example.

To guard against a solution that only works on the tiny public example, the repository also includes a deterministic robustness smoke test:

```bash
npm run official-robustness
```

It creates six larger variants from public example data and checks the candidate through the public official checker:

```text
variants=6
all_candidates_feasible=True
all_candidates_improve_greedy=True
synthetic_B2_b12 candidate=1512.370044 greedy=1812.553857 delta_vs_greedy=-300.183813
synthetic_B3_b14 candidate=1107.497693 greedy=2611.626011 delta_vs_greedy=-1504.128318
synthetic_B3_b16 candidate=1360.556393 greedy=1748.195903 delta_vs_greedy=-387.639509
synthetic_B3_b18 candidate=1887.910173 greedy=3744.245261 delta_vs_greedy=-1856.335089
synthetic_B3_b20 candidate=1813.328413 greedy=4472.911928 delta_vs_greedy=-2659.583515
synthetic_B3_b24 candidate=2529.572218 greedy=2847.708322 delta_vs_greedy=-318.136104
```

This is not official leaderboard evidence and it does not replace training, preliminary, or final instances. It is a regression guard showing that the candidate package stays checker-feasible and is no worse than the public greedy reference on larger public-example-derived inputs.

The repository can also build a candidate package for the official platform:

```bash
npm run official-package
```

Outputs:

```text
outputs/official_submission_candidate.zip
outputs/official_submission_manifest.json
```

The zip contains `myalgorithm.py` at the archive root. This is a readiness package and must be sent only through an allowed official OGC submission window.

## Boundary

This projection is not an official OGC solver result. It proves that the lab can ingest the official example schema and run the existing search pipeline over a simplified rectangle projection.

Still required for real competition work:

1. Keep the standalone `myalgorithm.py` package self-contained and checker-feasible.
2. Improve objective quality against official training/preliminary instances once they are released.
3. Add deeper placement-level search inside the import-free official candidate without depending on repo-local helper modules.
4. Use official training/preliminary instances when released.
5. Submit only through an allowed official OGC window and record the receipt.
