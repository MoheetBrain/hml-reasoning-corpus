# HML50K complexity audit

The frozen burden score is:

`n_hypotheses_before + n_goals_before + depth + target/context/goal field changes`.

TRAIN-only quartiles were fixed before rendering: q25=16, q50=23, q75=32. Mapping the
machine labels to the requested report vocabulary gives:

| report bin | machine bin | all rows |
|---|---|---:|
| LOW | EASY | 14,384 |
| MEDIUM | MEDIUM | 14,529 |
| HIGH | HARD | 13,951 |
| VERY_HIGH | LONG_OR_STRUCTURALLY_DENSE | 13,136 |

The 5,000-row structural-stress subset ranks unchanged records by the frozen burden plus
source premise, goal-count, and context-change signals. It contains 4,358 VERY_HIGH rows.
Branches, proof obligations distinct from goals, and VNext candidate lifecycle relations
remain unsupported by this source and are not synthesized. See
`audits/complexity_thresholds.json` and `structural_stress/manifest.json`.
