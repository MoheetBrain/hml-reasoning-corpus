# Gold-125 ontology-v1 saturation report

Exploratory evidence only; no asymptotic saturation claim is made.

| Trajectories | Transitions | Observed | Accepted core | New accepted core | Candidate core | Library | Meta | Warrants |
|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 25 | 118 | 48 | 15 | APPLY_DEFINITION, APPLY_THEOREM, BOUND, CASE_SPLIT, COUNT, DECLARE, DISCHARGE, ENUMERATE, EVALUATE, MODEL, RECORD, SELECT, SUBSTITUTE, TRANSFORM, VERIFY | 15 | 1 | 3 | 7 |
| 50 | 337 | 64 | 17 | CONSTRUCT, CONTRADICTION | 17 | 2 | 6 | 14 |
| 75 | 476 | 65 | 17 | none | 18 | 2 | 6 | 14 |
| 100 | 636 | 66 | 17 | none | 18 | 2 | 6 | 14 |
| 125 | 769 | 66 | 17 | none | 18 | 2 | 6 | 14 |

## Core top-k coverage

| k | Coverage | Units |
|---:|---:|---:|
| 5 | 80.2% | 626 |
| 10 | 94.9% | 626 |
| 15 | 99.5% | 626 |
| 20 | 100.0% | 626 |
| all | 100.0% | 626 |

Ontology-v1 does not carry the pre-cleanup count of 27 as sacred. It factors named warrants and orthogonal effects before counting reusable operations. Candidate operations excluded by adjudication remain visible in the derived view.
