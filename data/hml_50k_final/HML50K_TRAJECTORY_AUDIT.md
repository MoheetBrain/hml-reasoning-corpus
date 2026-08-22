# HML50K trajectory and depth audit

Result: `PASS`.

- 16,950 distinct parent theorems.
- 14,080 complete source trajectories: 5,897 multi-step and 8,183 single-step; 2,870
  partial trajectories after duplicate, leakage, character, and tokenizer exclusions.
- 0 predecessor-link errors; 0 successor-link errors.
- 9,202 records occur at depth 11 or later.

| depth | rows |
|---|---:|
| 1 | 15,532 |
| 2–3 | 13,731 |
| 4–5 | 8,045 |
| 6–10 | 9,490 |
| 11–20 | 6,295 |
| 21+ | 2,907 |

Every row retains parent membership, proof length, step index, selected trajectory steps,
and available predecessor/successor record IDs. Splits are parent-disjoint by official
LeanDojo train/val/test provenance. See `audits/trajectory_depth_audit.json`.
