# Reasoning failure atlas

## Population

All 3,000 old-FINAL rows are retained as discovery data. Counts: BOTH_CORRECT 2,513; NEUTRAL_ONLY 130; HML_ONLY 47; BOTH_WRONG 310.

The primary category is a deterministic evidence tag, not a claim that the model's hidden causal mechanism was observed. Candidate alternatives are `PLAUSIBLE_UNEXECUTED`; consequently `ACTION_APPLICABILITY` means within-family discrimination pressure, not verified invalidity of the rejected candidates.

## Evidence-backed primary categories

| category | rows | representative record IDs |
|---|---:|---|
| REPRESENTATION_COMPLEXITY | 177 | H50K-LEAN-0140f21681993b87, H50K-LEAN-02314a846e79931c, H50K-LEAN-02782ef109fca248, H50K-LEAN-02cddf5f1c9db7b6, H50K-LEAN-03a3406045deca37, H50K-LEAN-046f1d72453b743d, H50K-LEAN-06cba2af851a078a, H50K-LEAN-08f5c8cca33eed1b |
| ACTION_APPLICABILITY | 107 | H50K-LEAN-01095057e767b64c, H50K-LEAN-057dadbe5f63de83, H50K-LEAN-095552c27a221f08, H50K-LEAN-09fa62de3015999e, H50K-LEAN-0ec7e40e2fc94dd7, H50K-LEAN-0f0f4a5c30082f67, H50K-LEAN-10418f786dc90ab2, H50K-LEAN-1371f3c69b496067 |
| BRANCH_STATE | 93 | H50K-LEAN-02f29ed2deb0e7db, H50K-LEAN-06074d471b7e6597, H50K-LEAN-0d6f26ebfc5bc8f1, H50K-LEAN-124f3a6e760a87bf, H50K-LEAN-13699f55f98a0b3d, H50K-LEAN-14c767e389ebab06, H50K-LEAN-16940a8416a9f8c0, H50K-LEAN-1770ee56b1ac8911 |
| UNKNOWN | 62 | H50K-LEAN-000444eb979bbdc8, H50K-LEAN-01a6ba4e028c9eb5, H50K-LEAN-03777f6750abac9f, H50K-LEAN-05f4290335d0517d, H50K-LEAN-0b6c32bbfe29087f, H50K-LEAN-0d3372babe032879, H50K-LEAN-0d5e6bb5e478b800, H50K-LEAN-0e59dec50eca3bb2 |
| PREMISE_DEPENDENCY | 42 | H50K-LEAN-0243339925b0a3f5, H50K-LEAN-05f2816c607e13ab, H50K-LEAN-06af83d5bf30151f, H50K-LEAN-0a064676a269bb57, H50K-LEAN-1a613e2774c61670, H50K-LEAN-29ac74c819c2606d, H50K-LEAN-3a4d4d1f08f16915, H50K-LEAN-3d71dcab8014d0be |
| GOAL_SELECTION | 6 | H50K-LEAN-0b315decd4005e1b, H50K-LEAN-3ad87511a5549560, H50K-LEAN-64db2b4c483f0d16, H50K-LEAN-736080d9ad5e8754, H50K-LEAN-a693eb1dcdbfd9bc, H50K-LEAN-f3fccbf720b91cae |

## Primary-category counts by proof depth

| depth | UNKNOWN | ACTION_APPLICABILITY | REPRESENTATION_COMPLEXITY | PREMISE_DEPENDENCY | BRANCH_STATE | GOAL_SELECTION |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 14 | 50 | 35 | 8 | 0 | 0 |
| 2-5 | 39 | 29 | 75 | 17 | 45 | 4 |
| 6-10 | 3 | 10 | 28 | 9 | 21 | 1 |
| 11-20 | 6 | 13 | 27 | 6 | 22 | 1 |
| 21+ | 0 | 5 | 12 | 2 | 5 | 0 |

## Objective feature coverage

- BOTH_WRONG rows mined first: 310.
- Rows with source-explicit multiple goals: 21.
- Rows whose recorded tactic names a local declaration: 1,593.
- Rows with source-explicit `case` identity: 1,290.
- Rows with actual failed/invalid actions in passive history: 0.

Each machine row also records depth, parent, hypotheses, goal form, candidate/tactic families, trajectory position, recent actions and deltas, repeated actions, prompt lengths, lexical baseline, complexity, old/common predictions, hashes, taxonomy evidence and provenance limits.

## Unavailable categories

`SEARCH_LOOP` and failed-route memory cannot be diagnosed from these successful traces. `SCOPE_CONFUSION`, strategy state, and lemma/invariant roles are not assigned without stronger observable evidence. Such rows remain `UNKNOWN` or receive only a coarser source-supported tag.
