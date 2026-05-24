# Official Robustness Smoke Report

This report uses deterministic synthetic variants derived from the public OGC baseline example.

It is not official leaderboard evidence. It checks whether the candidate algorithm stays feasible and improves the public greedy reference when the public example is expanded in size.

## Results

| Variant | Blocks | Bays | Greedy objective | Candidate objective | Improvement | Candidate feasible |
|---|---:|---:|---:|---:|---:|---|
| synthetic_B2_b12 | 12 | 2 | 1812.553857 | 1366.056678 | 446.497179 | True |
| synthetic_B3_b14 | 14 | 3 | 2611.626011 | 1084.812759 | 1526.813252 | True |
| synthetic_B3_b16 | 16 | 3 | 1748.195903 | 901.905038 | 846.290865 | True |

## Boundary

These variants are deterministic stress checks created from public example data.
They do not replace official training, preliminary, final, or leaderboard instances.
The useful signal is regression safety: the candidate package remains official-checker feasible and beats the public greedy reference on all included variants.
