# HML50K source audit

The local inventory contains 4,311,789 rows before deduplication across related sources.
The model-facing core uses only the 241,265-row LeanDojo canonical transition export and
selects 56,000 exact `(state_before, tactic, state_after)` records from it.

| source | local rows | status | core rows | decision |
|---|---:|---|---:|---|
| LeanDojo canonical transitions | 241,265 | FORMAL_TRACE | 56,000 | exact task-native transition source |
| LeanDojo raw benchmark | 259,580 | FORMAL_TRACE | 0 | premise recovery and exact identity check only |
| STP_Lean_0320 | 3,262,558 | mixed formal proof/conjecturing | 0 | not traced state/action/after; 51,273 conjecturing rows |
| NuminaMath-LEAN | 104,155 | formal proof text | 0 | not traced state/action/after |
| Herald proofs | 44,553 | formal proof plus natural annotation | 0 | not traced state/action/after |
| state_tactic_pairs | 56,407 | state/action only | 0 | missing state_after |
| Pythagoras SFT | 126,113 | SFT proof text | 0 | not traced state/action/after |
| PRM800K | 101,599 files/trajectories | HUMAN_PROCESS_LABEL | 0 | kept separate from formal-trace truth status |
| Hendrycks MATH | 12,500 | worked solution, unverified here | 0 | no exact transition segmentation audit |
| AMPS/Khan | 103,059 | procedural text, unverified here | 0 | not promoted to fill a quota |

The preferred source proportions were not forced. Exact formal transitions already exceed
the 50K TRAIN gate; adding lower-certainty derived transitions would reduce semantic quality.
The full machine inventory is in `audits/source_inventory.json`; source exclusions and the
fresh-population census are in `audits/source_audit.json`.
