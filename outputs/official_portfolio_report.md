# Official Portfolio Smoke Report

This report uses the public OGC 2026 baseline package and official feasibility checker.

## Candidate Algorithm

- File: `official_submission/myalgorithm.py`
- Method: run the public greedy baseline, then search bay-assignment candidates and keep the best feasible official solution.
- Feasible: True
- Stage: 5
- Objective: 1022.6988257889582
- obj1 tardiness: 0.0
- obj2 imbalance: 14.671260826994029
- obj3 preference penalty: 46.0

## Public Greedy Reference

- Feasible: True
- Stage: 5
- Objective: 1055.7278963621302
- obj1 tardiness: 0.0
- obj2 imbalance: 19.3896994803043
- obj3 preference penalty: 46.0

## Delta

- Objective delta vs greedy: -33.029071
- Improvement: 33.029071

## Boundary

This is an official-example smoke test, not leaderboard evidence.
It proves that the repository now contains a checker-validated official-format algorithm candidate that improves over the public greedy reference on example_B2_b10.
