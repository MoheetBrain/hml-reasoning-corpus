# Reasoning-layer V1 FINAL_A report

## Final verdict

**`V1_SEMANTIC_COMPRESSION_FAILED`** on 1 seed(s). FINAL_B remains sealed and unopened.

| arm | Top-1 | 95% clustered CI | MRR | NLL | entropy | gold margin |
|---|---:|---:|---:|---:|---:|---:|
| BASE | 87.80% | [86.56, 89.03]% | 0.9280 | 0.4392 | 0.7745 | 2.4720 |
| RAW | 88.93% | [87.72, 90.14]% | 0.9336 | 0.4723 | 0.8799 | 2.1913 |
| SEMANTIC | 88.23% | [86.99, 89.52]% | 0.9286 | 0.4820 | 0.8699 | 2.3413 |

## Primary contrasts

- raw_minus_base: +1.13pp, 95% CI [+0.31, +2.04]pp.
- semantic_minus_base: +0.43pp, 95% CI [-0.32, +1.17]pp.
- semantic_minus_raw: -0.70pp, 95% CI [-1.64, +0.16]pp.


## Token economics

- BASE mean/median/p95/max: 363.1 / 319.0 / 691.0 / 3237.
- RAW mean/median/p95/max: 1136.5 / 766.0 / 3269.2 / 11546.
- SEMANTIC mean/median/p95/max: 904.0 / 816.0 / 1614.0 / 4868.
- Ratios RAW/BASE 3.130×, SEMANTIC/BASE 2.490×, SEMANTIC/RAW 0.795×. Zero truncation.

## SEMANTIC−RAW by depth

| depth | Top-1 delta |
|---|---:|
| 1 | +1.04pp |
| 2-3 | -1.70pp |
| 4-5 | -2.51pp |
| 6-10 | -2.02pp |
| 11-20 | +0.00pp |
| 21+ | +3.78pp |

The depth pattern is not monotonic: V1 trails RAW at depths 2–10, is tied at 11–20,
and leads only in the small 21+ stratum (185 rows). This does not establish increasing
benefit with reasoning depth.

## Module presence

| module | stratum | rows | SEMANTIC−RAW Top-1 | 95% clustered CI |
|---|---|---:|---:|---:|
| GOALS | present (universal) | 3,000 | -0.70pp | [-1.61, +0.17]pp |
| DEPENDENCIES | absent | 298 | +0.34pp | [-1.89, +2.64]pp |
| DEPENDENCIES | present | 2,702 | -0.81pp | [-1.81, +0.18]pp |
| BRANCH_SCOPE | absent | 1,623 | -0.74pp | [-1.96, +0.39]pp |
| BRANCH_SCOPE | present | 1,377 | -0.65pp | [-1.98, +0.67]pp |
| HISTORY | absent | 757 | +0.79pp | [-0.79, +2.51]pp |
| HISTORY | present | 2,243 | -1.20pp | [-2.31, -0.13]pp |

GOALS has no absent stratum in this Lean task, so its presence effect is not identifiable.
DEPENDENCIES shows a weak regression association, BRANCH_SCOPE shows no differential help,
and the clearest split is HISTORY: RAW's exact history beats V1's compressed history when
history exists. These are observational strata, not module ablations.

## Decision boundary

Organization gain is -0.70pp with CI [-1.64, +0.16]pp. Seed 2 status: `NOT_AUTHORIZED`. Module-presence and information-loss diagnostics are machine-readable under `diagnostics/`; no module was retrained and V1 was not edited.
