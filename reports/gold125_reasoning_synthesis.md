# Gold-125 reasoning synthesis

This is a semantic-discovery synthesis over the frozen Gold-25 plus exactly 100 new source-grounded trajectories. It is not a training corpus, HML benchmark, or claim of formal proof replay.

## A. Corpus size and transition accounting

- Total trajectories: 125 (frozen old: 25; new: 100)
- Total source-granularity transitions: 769 (old: 118; new: 651)
- Atomic source steps: 556
- Compound macros: 89
- Uncertain atomicity: 124
- Normalized atomic units: 730

## B. Explicit versus reconstructed implicit transitions

- Explicit source-supported transitions: 749
- Implicit/formula-continuation transitions: 20

## C-F. Operation counts

- Observed source-granularity operation IDs: 66
- Normalized atomic operation IDs: 28
- Candidate CORE operation IDs: 27
- Singleton/doubleton observed labels: 36
- New candidate core IDs relative to Gold-25: none

## G. Operation frequency distribution

| Observed operation | Frequency | Candidate core | Layer |
|---|---:|---|---|
| TRANSFORM | 200 | TRANSFORM | CORE_PROOF_OPERATION |
| OTHER | 125 | UNRESOLVED | UNRESOLVED |
| DISCHARGE | 87 | DISCHARGE | CORE_PROOF_OPERATION |
| EVALUATE | 30 | EVALUATE | NUMERIC_BACKEND_OPERATION |
| APPLY_THEOREM | 29 | APPLY_THEOREM | CORE_PROOF_OPERATION |
| MODULAR_REASONING | 26 | MODULAR_REASONING | DOMAIN_LIBRARY |
| VERIFY | 24 | VERIFY | CORE_PROOF_OPERATION |
| SEQUENCE_RECURRENCE | 23 | SEQUENCE_RECURRENCE | DOMAIN_LIBRARY |
| TRIG_IDENTITY | 23 | TRIG_IDENTITY | DOMAIN_LIBRARY |
| APPLY_DEFINITION | 19 | APPLY_DEFINITION | CORE_PROOF_OPERATION |
| OPTIMIZE | 17 | OPTIMIZE | CORE_PROOF_OPERATION |
| CASE_SPLIT | 15 | CASE_SPLIT | CORE_PROOF_OPERATION |
| COUNT | 12 | COUNT | DOMAIN_LIBRARY |
| PROBABILITY | 12 | PROBABILITY | DOMAIN_LIBRARY |
| CONSTRUCT | 9 | CONSTRUCT | CORE_STATE_OPERATION |
| INDUCT | 7 | INDUCT | CORE_PROOF_OPERATION |
| SEARCH_META | 7 | SEARCH_META | SEARCH_META_OPERATION |
| SUBSTITUTE | 7 | SUBSTITUTE | CORE_PROOF_OPERATION |
| CONTRADICTION | 6 | CONTRADICTION | CORE_PROOF_OPERATION |
| FORMULATE_EQUATION | 6 | MODEL | CORE_STATE_OPERATION |
| SOLVE | 6 | TRANSFORM | CORE_PROOF_OPERATION |
| INTRODUCE_VARIABLE | 5 | DECLARE | CORE_STATE_OPERATION |
| COUNT_CASES | 4 | UNRESOLVED | UNRESOLVED |
| EXPAND | 4 | TRANSFORM | SYMBOLIC_BACKEND_OPERATION |
| VERIFY_CANDIDATE | 4 | VERIFY | CORE_PROOF_OPERATION |
| COMBINE_CASE_COUNTS | 3 | COUNT | DOMAIN_LIBRARY |
| CONDITIONAL_PROBABILITY | 3 | EVALUATE | DOMAIN_LIBRARY |
| DISCHARGE_GOAL | 3 | DISCHARGE | CORE_PROOF_OPERATION |
| FACTOR | 3 | TRANSFORM | SYMBOLIC_BACKEND_OPERATION |
| SELECT_CANDIDATE | 3 | SELECT | CORE_PROOF_OPERATION |
| ADD_BOTH_SIDES | 2 | TRANSFORM | CORE_PROOF_OPERATION |
| APPLY_IDENTITY | 2 | APPLY_THEOREM | THEOREM_LIBRARY |
| BOUND | 2 | BOUND | CORE_PROOF_OPERATION |
| BOUND_REASONING | 2 | BOUND | CORE_PROOF_OPERATION |
| BOUND_SEARCH | 2 | SEARCH_META | SEARCH_META_OPERATION |
| COMPLEMENT_COUNT | 2 | COUNT | DOMAIN_LIBRARY |
| COUNT_PERMUTATIONS | 2 | COUNT | DOMAIN_LIBRARY |
| ENUMERATE | 2 | ENUMERATE | SEARCH_META_OPERATION |
| EVALUATE_PROBABILITY | 2 | EVALUATE | DOMAIN_LIBRARY |
| INCLUSION_EXCLUSION | 2 | INCLUSION_EXCLUSION | THEOREM_LIBRARY |
| SOLVE_CASE | 2 | TRANSFORM | CORE_PROOF_OPERATION |
| ADVANCE_SEQUENCE | 1 | TRANSFORM | DOMAIN_LIBRARY |
| APPLY_PRECEDENCE | 1 | APPLY_DEFINITION | CORE_PROOF_OPERATION |
| CANCEL_SYMMETRIC_TERMS | 1 | TRANSFORM | CORE_PROOF_OPERATION |
| CLEAR_DENOMINATOR | 1 | TRANSFORM | CORE_PROOF_OPERATION |
| COMBINE_CASES | 1 | UNRESOLVED | UNRESOLVED |
| COMBINE_LIKE_TERMS | 1 | TRANSFORM | CORE_PROOF_OPERATION |
| CONSTRAINT_PROPAGATION | 1 | TRANSFORM | CORE_PROOF_OPERATION |
| COUNT_EXCLUDED | 1 | COUNT | DOMAIN_LIBRARY |
| CROSS_MULTIPLY | 1 | TRANSFORM | CORE_PROOF_OPERATION |
| DIFFERENTIATE | 1 | DIFFERENTIATE | DOMAIN_LIBRARY |
| DIVIDE_BOTH_SIDES | 1 | TRANSFORM | CORE_PROOF_OPERATION |
| EXTRACT_ROOT | 1 | TRANSFORM | CORE_PROOF_OPERATION |
| FORMULATE_INEQUALITY | 1 | MODEL | CORE_STATE_OPERATION |
| INDEX_TRANSLATION | 1 | TRANSFORM | DOMAIN_LIBRARY |
| MULTIPLY_CONDITIONALS | 1 | EVALUATE | DOMAIN_LIBRARY |
| MULTIPLY_COUNTS | 1 | COUNT | DOMAIN_LIBRARY |
| PARAMETERIZE_CONGRUENCE | 1 | TRANSFORM | DOMAIN_LIBRARY |
| PRIME_FACTORIZE | 1 | TRANSFORM | DOMAIN_LIBRARY |
| RATIONALIZE | 1 | TRANSFORM | SYMBOLIC_BACKEND_OPERATION |
| RECORD_EQUALITY_CONDITION | 1 | RECORD | CORE_PROOF_OPERATION |
| RECORD_GIVEN | 1 | RECORD | CORE_STATE_OPERATION |
| ROUND_TO_DOMAIN | 1 | UNRESOLVED | UNRESOLVED |
| SELECT_EXTREMUM | 1 | SELECT | CORE_PROOF_OPERATION |
| SUBTRACT_BOTH_SIDES | 1 | TRANSFORM | CORE_PROOF_OPERATION |
| TAKE_LIMIT | 1 | TAKE_LIMIT | DOMAIN_LIBRARY |

## H. Saturation curve

| Trajectories | Observed ops | Atomic ops | Candidate core ops | New core ops | New library ops | New state fields | New gap classes |
|---:|---:|---:|---:|---|---|---|---|
| 25 | 48 | 17 | 16 | APPLY_DEFINITION, APPLY_THEOREM, BOUND, CASE_SPLIT, COUNT, DECLARE, DISCHARGE, ENUMERATE, EVALUATE, MODEL, RECORD, SEARCH_META, SELECT, SUBSTITUTE, TRANSFORM, VERIFY | ADVANCE_SEQUENCE, APPLY_IDENTITY, APPLY_THEOREM, COMBINE_CASE_COUNTS, COMPLEMENT_COUNT, CONDITIONAL_PROBABILITY, COUNT_EXCLUDED, COUNT_PERMUTATIONS, EVALUATE_PROBABILITY, EXPAND, FACTOR, INDEX_TRANSLATION, MULTIPLY_CONDITIONALS, MULTIPLY_COUNTS, PARAMETERIZE_CONGRUENCE, PRIME_FACTORIZE, RATIONALIZE | assumptions, constraints, declarations, definitions, dependencies, discharged_obligations, epistemic_status, facts, goals, id, objects, open_obligations, scope, subgoals, types_domains | MATH-GAP-0001, MATH-GAP-0002, MATH-GAP-0003, MATH-GAP-0004, MATH-GAP-0005, MATH-GAP-0006, MATH-GAP-0007, MATH-GAP-0008, MATH-GAP-0009, MATH-GAP-0010 |
| 50 | 64 | 27 | 26 | CONSTRUCT, CONTRADICTION, DIFFERENTIATE, INCLUSION_EXCLUSION, MODULAR_REASONING, OPTIMIZE, PROBABILITY, SEQUENCE_RECURRENCE, TAKE_LIMIT, TRIG_IDENTITY | COUNT, DIFFERENTIATE, EVALUATE, INCLUSION_EXCLUSION, MODULAR_REASONING, PROBABILITY, SEQUENCE_RECURRENCE, TAKE_LIMIT, TRIG_IDENTITY | branch_state, candidates | MATH-GAP-0011, MATH-GAP-0013 |
| 75 | 65 | 28 | 27 | INDUCT | none | none | MATH-GAP-0012 |
| 100 | 66 | 28 | 27 | none | none | none | none |
| 125 | 66 | 28 | 27 | none | none | none | none |

Interpretation: observed labels continue to grow because domain procedures and surface distinctions are numerous. The candidate-core curve should be read separately; it measures generic semantic roles, not names of mathematical theorems. Gold-125 is still too small to prove asymptotic saturation.

## I. Top-k coverage curve

| k | All normalized operations | Core proof/state operations |
|---:|---:|---:|
| 5 | 61.4% | 72.5% |
| 10 | 80.1% | 85.8% |
| 15 | 91.5% | 95.1% |
| 20 | 97.0% | 99.6% |
| 30 | 100.0% | 100.0% |
| all | 100.0% | 100.0% |

## J. Long tail

See reports/operation_long_tail_analysis_gold125.md. The long tail is dominated by domain/library labels, backend procedures, and source-specific meta choices rather than evidence for one bespoke core instruction per label.

## K. HML support distribution

| HML support | Source steps | Fraction |
|---|---:|---:|
| FULL | 11 | 1.4% |
| PARTIAL | 455 | 59.2% |
| REPRESENTABLE_ONLY | 303 | 39.4% |
| ABSENT | 0 | 0.0% |
| UNKNOWN | 0 | 0.0% |

See reports/gold125_hml_coverage.md for normalized atomic and domain-specific views.

## L. Semantic gaps

- MATH-GAP-0003: 204 step references; class CORE_SEMANTIC_MISSING
- MATH-GAP-0009: 179 step references; class LIBRARY_MISSING
- MATH-GAP-0008: 121 step references; class LIBRARY_MISSING
- MATH-GAP-0004: 107 step references; class CORE_SEMANTIC_MISSING
- MATH-GAP-0007: 71 step references; class LIBRARY_MISSING
- MATH-GAP-0002: 47 step references; class CORE_SEMANTIC_MISSING
- MATH-GAP-0010: 37 step references; class TRAJECTORY_SCHEMA_PROBLEM
- MATH-GAP-0001: 22 step references; class CORE_SEMANTIC_MISSING
- MATH-GAP-0006: 18 step references; class LIBRARY_MISSING
- MATH-GAP-0011: 7 step references; class TRANSLATION/CANONICALIZATION_PROBLEM
- MATH-GAP-0012: 7 step references; class CORE_SEMANTIC_MISSING
- MATH-GAP-0005: 5 step references; class LIBRARY_MISSING
- MATH-GAP-0013: 2 step references; class LIBRARY_MISSING

See reports/gold125_gap_analysis.md and the updated registry under schemas/gold125_gap_registry_v1.json.

## M. Preconditions

- Total precondition records: 340
- Status distribution: {'satisfied': 24, 'implicit': 10, 'UNKNOWN': 199, 'EXPLICIT_SOURCE': 107}
- Source-omission/unknown records: 199

The expansion records unknown applicability risks rather than inventing unstated domain conditions.

## N. Obligations

- Obligations created: 257
- With measured lifetime: 243
- Mean measured lifetime: 2.54 steps
- Maximum measured lifetime: 13 steps
- Immediately discharged: 48
- Open at final state: 8

Gold-25 immediate-discharge records are retained as frozen evidence; new trajectories expose lifetime fields explicitly.

## O. Dependency graph statistics

- Dependency edges: 901
- Maximum fan-in: 11
- Trajectories: 125
- Facts reused by multiple later steps: computed in reports/gold125_dependency_graph.json

## P. Branch and scope statistics

- Trajectories with branch-local steps: 5/125
- Branch-local steps: 26
- Maximum branch depth: 1
- Explicit branch joins: 1
- CASE_SPLIT-labelled steps: 15
- Invariant joins certified: 0 (not inferred)
- Exhaustive partitions certified: 0 (not inferred)

The builder records explicit branch joins but does not infer invariant proofs or exhaustive/disjoint partition certificates from textbook prose.

## Q. Search/meta-reasoning statistics

- Mode counts: {'EXECUTION': 580, 'VERIFICATION': 28, 'GOAL_MANAGEMENT': 113, 'SEARCH_META': 48}
- Independent hard audits: 15
- Explicit meta records: 82 new plus source-cue scan over old

See reports/thinking_vs_execution_gold125.md.

## R. State-field usage

- State fields observed: assumptions, branch_state, candidates, constraints, declarations, definitions, dependencies, discharged_obligations, epistemic_status, facts, goals, id, objects, open_obligations, scope, subgoals, types_domains

See reports/gold125_state_profile.md. Candidate and branch_state are added to the new schema; no Gold-25 state was changed.

## S. Source-solution quality

- Original problem and solution text are preserved verbatim for all new records.
- Every new result statement equals its exact motivating source span.
- Unknown conditions and compound macros are explicit metadata, not silently repaired.
- Successful source solutions do not expose failed search attempts.

## T. Architecture implications

H1 — STATE-TRANSITION THESIS: STRONG GO. Across 125 trajectories, S_t -> a_t -> S_{t+1} preserves facts, provenance, goals, scope, obligations, and source evidence usefully.
H2 — SMALL-CORE THESIS: GO. Many observed labels collapse into a compact generic candidate core, but the core curve has not mathematically saturated.
H3 — HML-SEMANTICS THESIS: GO. Current HML has the right typed-state/proof boundary; missing support is mostly generic interfaces, theorem libraries, and backends.
H4 — THINKING-LANGUAGE THESIS: INCONCLUSIVE / HYBRID. Positive source-visible meta-reasoning exists, but successful solutions cannot measure open-ended search. Evidence favors a proposer/planner plus checked trajectory.
H5 — LEARNED-REPRESENTATION THESIS: NOT TESTED. No neural or representation comparison was performed.

## Provisional V1 assessment

Proceed with Gold-125 as a saturation/search-language audit, not as a training or benchmark corpus. Do not modify HML core until the gap/library/meta evidence is reviewed. The next experiment should independently annotate a smaller hard subset with a human mathematical audit and compare source-grounded extraction against a richer structured proposer.

## Stop condition

Gold-125 is complete. Problem 126 was not processed. No additional dataset or training work is authorized by this mission.
