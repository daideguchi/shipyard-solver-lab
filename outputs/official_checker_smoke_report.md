# Official Checker Smoke Report

This report uses the public OGC 2026 baseline package and the official feasibility checker.

## Simple Sequential Submission

- Purpose: prove exact official solution format and checker integration.
- Feasible: True
- Stage: 5
- Objective: 281320.78620320855
- obj1 tardiness: 105.0
- obj2 imbalance: 183.68374331550805
- obj3 preference penalty: 0.0

## Official Greedy Reference

- Purpose: provide a public baseline from the organizer package.
- Feasible: True
- Stage: 5
- Objective: 1055.7278963621302
- obj1 tardiness: 0.0
- obj2 imbalance: 19.3896994803043
- obj3 preference penalty: 46.0

## Boundary

The simple sequential solution is not competitive. It is intentionally conservative.
The next real scoring step is to replace it with an optimized official-format algorithm while keeping the official checker green.
