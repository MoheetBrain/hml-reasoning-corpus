# Gold-25 reasoning synthesis

## A. Operation frequency table

| Operation | Frequency |
|---|---:|
| `EVALUATE` | 12 |
| `INTRODUCE_VARIABLE` | 7 |
| `APPLY_DEFINITION` | 7 |
| `FORMULATE_EQUATION` | 6 |
| `SOLVE` | 6 |
| `CASE_SPLIT` | 5 |
| `SUBSTITUTE` | 5 |
| `EXPAND` | 4 |
| `VERIFY_CANDIDATE` | 4 |
| `APPLY_THEOREM` | 4 |
| `COUNT_CASES` | 4 |
| `DISCHARGE_GOAL` | 3 |
| `FACTOR` | 3 |
| `COMBINE_CASE_COUNTS` | 3 |
| `CONDITIONAL_PROBABILITY` | 3 |
| `SELECT_CANDIDATE` | 3 |
| `APPLY_IDENTITY` | 2 |
| `SOLVE_CASE` | 2 |
| `COMPLEMENT_COUNT` | 2 |
| `ENUMERATE` | 2 |
| `COUNT_PERMUTATIONS` | 2 |
| `EVALUATE_PROBABILITY` | 2 |
| `BOUND_SEARCH` | 2 |
| `RECORD_GIVEN` | 1 |
| `EXTRACT_ROOT` | 1 |
| `CROSS_MULTIPLY` | 1 |
| `ADD_BOTH_SIDES` | 1 |
| `DIVIDE_BOTH_SIDES` | 1 |
| `SELECT_EXTREMUM` | 1 |
| `COMBINE_LIKE_TERMS` | 1 |
| `RECORD_EQUALITY_CONDITION` | 1 |
| `MULTIPLY_CONDITIONALS` | 1 |
| `BOUND_REASONING` | 1 |
| `CONSTRAINT_PROPAGATION` | 1 |
| `MULTIPLY_COUNTS` | 1 |
| `PARAMETERIZE_CONGRUENCE` | 1 |
| `COUNT_EXCLUDED` | 1 |
| `INDEX_TRANSLATION` | 1 |
| `ADVANCE_SEQUENCE` | 1 |
| `PRIME_FACTORIZE` | 1 |
| `RATIONALIZE` | 1 |
| `CLEAR_DENOMINATOR` | 1 |
| `COMBINE_CASES` | 1 |
| `CANCEL_SYMMETRIC_TERMS` | 1 |
| `APPLY_PRECEDENCE` | 1 |
| `FORMULATE_INEQUALITY` | 1 |
| `SUBTRACT_BOTH_SIDES` | 1 |
| `ROUND_TO_DOMAIN` | 1 |

## B. Unique operations discovered

**48** distinct operation IDs appear in **118** canonical transitions. The catalogue is provisional and intentionally separates generic operations from domain theorems.

## C. Operation families

- `ALGEBRAIC_TRANSFORMATION`: 14 steps
- `EVALUATION`: 13 steps
- `CASE_ANALYSIS`: 10 steps
- `PROBABILISTIC_REASONING`: 9 steps
- `THEOREM_APPLICATION`: 8 steps
- `COMBINATORIAL_REASONING`: 7 steps
- `NUMBER_THEORY`: 7 steps
- `DECLARATION`: 6 steps
- `EQUATION_CONSTRUCTION`: 6 steps
- `EQUATION_TRANSFORMATION`: 6 steps
- `CONSTRAINT_REASONING`: 6 steps
- `DEFINITION_APPLICATION`: 5 steps
- `VERIFICATION`: 4 steps
- `GOAL_MANAGEMENT`: 4 steps
- `SUBSTITUTION`: 4 steps
- `CONSTRUCTION`: 3 steps
- `SEQUENCE_REASONING`: 3 steps
- `INEQUALITY_TRANSFORMATION`: 2 steps
- `STATE`: 1 steps

## D. HML coverage

| HML support status | Steps |
|---|---:|
| `FULL` | 10 |
| `PARTIAL` | 37 |
| `REPRESENTABLE_ONLY` | 71 |
| `ABSENT` | 0 |
| `UNKNOWN` | 0 |

The strict fully-supported step coverage is **10/118 = 8.5%**. This is a discovery metric, not a benchmark score; `PARTIAL` means the state/form or a local suboperation exists but the complete semantic transition does not.

## E. Gap distribution

- `DOMAIN_LIBRARY` / MATH-GAP-0007: 25 step references
- `DOMAIN_LIBRARY` / MATH-GAP-0008: 22 step references
- `LIBRARY_THEOREM` / MATH-GAP-0006: 18 step references
- `DOMAIN_LIBRARY` / MATH-GAP-0009: 15 step references
- `CORE_REASONING_OPERATION` / MATH-GAP-0001: 12 step references
- `CORE_STATE_REPRESENTATION` / MATH-GAP-0010: 7 step references
- `OBLIGATION_SYSTEM` / MATH-GAP-0004: 6 step references
- `VERIFIER_GAP` / MATH-GAP-0002: 6 step references
- `PRECONDITION_SYSTEM` / MATH-GAP-0003: 5 step references
- `LIBRARY_THEOREM` / MATH-GAP-0005: 3 step references

## F. Most important semantic gaps

1. Explicit exhaustive case splitting and branch merge (MATH-GAP-0001): recurs across absolute values, roots, dice, and complex candidates.
2. Domain/precondition and proof-debt handling (MATH-GAP-0003/0004): source solutions often rely on conditions that are not stated or discharged as separate objects.
3. Theorem/domain library interface (MATH-GAP-0005/0007/0008/0009): most mathematical knowledge is reusable library content, not a reason to grow the core rule registry.
4. Candidate verification (MATH-GAP-0002): textbook solutions frequently generate candidates and only later check them.
5. Sequence/exclusion representation (MATH-GAP-0010): discrete index shifts need explicit state, but recurrence across larger data is still untested.

## G. State content analysis

- `objects` appears in 25/25 trajectories
- `declarations` appears in 24/25 trajectories
- `types_domains` appears in 25/25 trajectories
- `facts` appears in 25/25 trajectories
- `assumptions` appears in 0/25 trajectories
- `constraints` appears in 1/25 trajectories
- `definitions` appears in 0/25 trajectories
- `goals` appears in 25/25 trajectories
- `subgoals` appears in 0/25 trajectories
- `dependencies` appears in 25/25 trajectories
- `open_obligations` appears in 0/25 trajectories
- `scope` appears in 25/25 trajectories

Facts and goals are universal in this deliberately problem-centered sample. Dependencies are present in every generated state because the trajectory preserves why each result exists. Assumptions and branch scope are common but not universal; obligations are sparse in the source but disproportionately important when transformations are non-reversible.

## H. Reasoning depth

| Problem | Source steps | Canonical steps | Explicit | Implicit | Max dependency depth (approx.) | Branches | Obligations |
|---|---:|---:|---:|---:|---:|---:|---:|
| MATH-GOLD-001 | 6 | 6 | 6 | 0 | 2 | 0 | 0 |
| MATH-GOLD-002 | 5 | 4 | 4 | 0 | 2 | 0 | 1 |
| MATH-GOLD-003 | 3 | 4 | 4 | 0 | 1 | 0 | 1 |
| MATH-GOLD-004 | 7 | 6 | 4 | 2 | 2 | 2 | 1 |
| MATH-GOLD-005 | 4 | 5 | 5 | 0 | 1 | 0 | 0 |
| MATH-GOLD-006 | 1 | 4 | 3 | 1 | 1 | 0 | 0 |
| MATH-GOLD-007 | 9 | 6 | 4 | 2 | 2 | 0 | 0 |
| MATH-GOLD-008 | 1 | 2 | 2 | 0 | 2 | 0 | 0 |
| MATH-GOLD-009 | 1 | 4 | 4 | 0 | 1 | 0 | 0 |
| MATH-GOLD-010 | 2 | 3 | 2 | 1 | 2 | 0 | 0 |
| MATH-GOLD-011 | 7 | 6 | 6 | 0 | 2 | 0 | 0 |
| MATH-GOLD-012 | 10 | 8 | 8 | 0 | 2 | 2 | 1 |
| MATH-GOLD-013 | 3 | 4 | 4 | 0 | 1 | 0 | 0 |
| MATH-GOLD-014 | 4 | 4 | 4 | 0 | 2 | 0 | 0 |
| MATH-GOLD-015 | 6 | 6 | 6 | 0 | 2 | 0 | 0 |
| MATH-GOLD-016 | 3 | 3 | 3 | 0 | 1 | 0 | 0 |
| MATH-GOLD-017 | 5 | 5 | 5 | 0 | 1 | 0 | 0 |
| MATH-GOLD-018 | 2 | 4 | 4 | 0 | 1 | 0 | 0 |
| MATH-GOLD-019 | 5 | 6 | 6 | 0 | 2 | 2 | 1 |
| MATH-GOLD-020 | 2 | 4 | 2 | 2 | 2 | 0 | 0 |
| MATH-GOLD-021 | 9 | 6 | 6 | 0 | 2 | 0 | 0 |
| MATH-GOLD-022 | 5 | 4 | 3 | 1 | 1 | 0 | 0 |
| MATH-GOLD-023 | 2 | 3 | 2 | 1 | 1 | 0 | 0 |
| MATH-GOLD-024 | 5 | 5 | 3 | 2 | 1 | 0 | 0 |
| MATH-GOLD-025 | 5 | 6 | 5 | 1 | 2 | 0 | 1 |

## I. Source quality

- Explicit reconstructed steps: **105**
- Implicit reconstructed steps: **13**
- Explicitly recorded source omissions/precondition omissions: **13**
- Solutions with alternative paths: **2**

The worked solutions are mathematically useful but compress semantic work. In particular, theorem hypotheses, domain restrictions, branch coverage, candidate verification, and minimality arguments are often implicit. Those omissions are recorded rather than silently repaired.

## Main discovery

The recurring pattern is not a vocabulary list of textbook phrases. It is a compact transition shape: typed objects and constraints, a reusable operation, a warrant/library reference, applicability conditions, proof debt, dependency edges, and a result that must be checked. Current HML already captures the local checked-kernel half of this shape; Gold-25 evidence points primarily toward branch/candidate interfaces and replayable mathematical libraries.
