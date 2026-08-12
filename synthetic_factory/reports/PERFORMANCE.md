# Performance benchmark

The same 1,000 ordered pair-verification tasks were executed for every worker
count. Each task imports and checks both the original and counterfactual transition in
a process-isolated scratch directory. All scratch directories were removed afterward.

| Workers | Wall s | Pairs/s | Verifications/s | Aggregate CPU | Allocated CPU | Peak child RSS KiB | Failures |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 0.134 | 7488.5 | 14976.9 | 353.9% | 88.5% | 37060 | 0 |
| 8 | 0.105 | 9519.3 | 19038.6 | 711.9% | 89.0% | 37060 | 0 |
| 16 | 0.117 | 8580.6 | 17161.1 | 1405.1% | 87.8% | 37060 | 0 |
| 20 | 0.138 | 7233.7 | 14467.5 | 1597.6% | 79.9% | 37060 | 0 |

- Deterministic result across worker counts: **true**
- Selected stable worker count: **8**
- Result SHA-256: `52d7ab578250ab58c083733ab3ce4b0cc9235c98e88f176dc7dc65c4ee686d56`

`ru_maxrss` is the operating system's peak-child statistic, not a sum across workers.
The chosen setting is empirical for this VM and is not encoded as a semantic default.
