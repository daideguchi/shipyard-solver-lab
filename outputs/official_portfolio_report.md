# Official Portfolio Smoke Report

This report uses the public OGC 2026 baseline package and official feasibility checker.

## Candidate Algorithm

- File: `official_submission/myalgorithm.py`
- Method: standalone import-free official-format solver with conservative bounding-box placement and official checker validation.
- Feasible: True
- Stage: 5
- Objective: 1055.7278963621302
- obj1 tardiness: 0.0
- obj2 imbalance: 19.3896994803043
- obj3 preference penalty: 46.0

## Public Greedy Reference

- Feasible: True
- Stage: 5
- Objective: 1055.7278963621302
- obj1 tardiness: 0.0
- obj2 imbalance: 19.3896994803043
- obj3 preference penalty: 46.0

## Delta

- Objective delta vs greedy: 0.0
- Match or better than greedy: True

## Boundary

This is an official-example smoke test, not leaderboard evidence.
It proves that the submitted single-file candidate is checker-feasible and no worse than the public greedy reference on example_B2_b10.
The official platform extracts only myalgorithm.py, so this smoke test prioritizes import-free submission safety over local-only helper modules.
