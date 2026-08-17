# Structural Leakage Audit

Status: **NOT APPLICABLE TO MODEL VIEWS — none were emitted**.

The source audit nevertheless enforced two leakage boundaries:

1. 3,670 old VNext/Qwen development parent groups were loaded from the frozen audit;
   42,957 raw transitions were excluded. No fresh FINAL split was created, so its
   overlap count is not misreported as a pass.
2. LeanDojo `annotated_tactic[1]` contains global declarations selected/used by the
   gold action. Although 141,075 fresh transitions have a non-empty list, those
   declarations were not promoted to input dependencies. The older canonical
   builder's empty `premises_used` field was a parsing defect, not permission to
   leak the corrected oracle.

| Required model-view control | Result |
|---|---|
| target-in-prompt detector | not run; no prompts |
| planted target control | not run; no prompts |
| position-only baseline | not run; no candidate sets |
| length-only baseline | not run; no candidate sets |
| tactic-family-only baseline | not run; no candidate sets |
| lexical name-overlap heuristic | not run; no candidate sets |
| randomized labels | not run; no labels |
| train/FINAL theorem overlap | not applicable; no split |

