# Structural Complexity Specification

Status: **frozen before model evaluation**, 2026-08-17. No model evaluation was
run.

For an admitted state, retain these raw external-state burden components:

| Symbol | Component |
|---|---|
| `H` | active non-branch-local hypotheses/facts |
| `G` | active goals/subgoals |
| `D` | explicit dependency edges |
| `d` | longest explicit dependency chain |
| `O` | open obligations distinct from goals |
| `S` | maximum active scope depth beyond the root |
| `B` | active branches with predicate and coverage metadata |
| `BL` | branch-local facts |
| `C` | candidates with lifecycle/status |
| `T` | zero-based trajectory depth |
| `Δ` | semantic state fields changed by the transition |

The unweighted burden score is:

`H + G + D + d + O + S + B + BL + C + T + Δ`

No learned or post-result weights are permitted. `H` excludes `BL` to avoid double
counting. Every raw component remains in the record; the scalar is only a grouping
aid.

Bins would be tie-aware quartiles of burden score computed from **admitted train
parents only**: `LOW`, `MEDIUM`, `HIGH`, `VERY_HIGH`. The cut points would be frozen
before any model result and applied unchanged to dev and FINAL. If ties make a
quartile boundary impossible, the boundary moves upward to keep identical scores in
one bin and the realized counts are reported.

Because the admission population gate failed, there is no admitted training
population from which to calculate honest cut points. No complexity labels were
assigned. Counts are `LOW=0`, `MEDIUM=0`, `HIGH=0`, `VERY_HIGH=0`.

