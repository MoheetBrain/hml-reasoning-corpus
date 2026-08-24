# Semantic module screen

Discovery-only screening predicts the next recorded tactic family, not the six-way confirmatory label. It is a cheap attribution proxy and cannot support a headline claim.

BASE lexical probe: 23.80%. FULL semantics: 28.40% (+4.60pp).

| module | prevalence | approx tokens | tagged error rows | MI bits | probe delta | decision |
|---|---:|---:|---:|---:|---:|---|
| GOALS | 100.00% | 99.8 | 8 | 0.8034 | +1.07pp | KEEP_V1 |
| DEPENDENCIES | 89.67% | 123.0 | 91 | 0.3827 | -0.50pp | KEEP_V1 |
| BRANCH_SCOPE | 43.00% | 11.5 | 213 | 0.0778 | +0.40pp | KEEP_V1 |
| HISTORY | 70.43% | 137.0 | 0 | 1.3853 | +3.57pp | KEEP_V1 |

## Keep/drop boundary

Admitted: GOALS, DEPENDENCIES, BRANCH_SCOPE, HISTORY. Obligations, verified search memory and lemma/invariant roles are dropped because the source cannot support them. No 2K/5K model screen or new training was run.

The final data renderer remains decomposable into GOALS, DEPENDENCIES, BRANCH_SCOPE and HISTORY so `FULL minus module` ablations remain possible without changing the ontology.
