# Official Robustness Smoke Report

This report uses deterministic synthetic variants derived from the public OGC baseline example.

It is not official leaderboard evidence. It checks whether the standalone candidate stays feasible and matches or improves the public greedy reference when the public example is expanded in size.

## Results

| Variant | Blocks | Bays | Greedy objective | Candidate objective | Delta vs greedy | Match or better | Candidate feasible |
|---|---:|---:|---:|---:|---:|---|---|
| synthetic_B2_b12 | 12 | 2 | 1812.553857 | 1512.370044 | -300.183813 | True | True |
| synthetic_B3_b14 | 14 | 3 | 2611.626011 | 1107.497693 | -1504.128318 | True | True |
| synthetic_B3_b16 | 16 | 3 | 1748.195903 | 1360.556393 | -387.639509 | True | True |
| synthetic_B3_b18 | 18 | 3 | 3744.245261 | 1183.073511 | -2561.171751 | True | True |
| synthetic_B3_b20 | 20 | 3 | 4472.911928 | 1532.799001 | -2940.112927 | True | True |
| synthetic_B3_b24 | 24 | 3 | 2847.708322 | 2215.626445 | -632.081876 | True | True |

## Boundary

These variants are deterministic stress checks created from public example data.
They do not replace official training, preliminary, final, or leaderboard instances.
The useful signal is regression safety: the single-file candidate remains official-checker feasible and is no worse than the public greedy reference on all included variants.
