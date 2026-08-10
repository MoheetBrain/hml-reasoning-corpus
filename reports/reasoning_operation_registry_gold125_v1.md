# Gold-125 normalized operation ontology

Observed labels are preserved. Candidate core primitives are hypotheses supported by recurrence and cross-domain reuse; they are not forced equivalences.

| Observed operation | Frequency | Candidate core | Layer | Atomicity | Domains |
|---|---:|---|---|---|---|
| TRANSFORM | 200 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:190, COMPOUND_MACRO:10 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus |
| OTHER | 125 | UNRESOLVED | UNRESOLVED | UNCERTAIN:124, COMPOUND_MACRO:1 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus |
| DISCHARGE | 87 | DISCHARGE | CORE_PROOF_OPERATION | ATOMIC:72, COMPOUND_MACRO:15 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus |
| EVALUATE | 30 | EVALUATE | NUMERIC_BACKEND_OPERATION | ATOMIC:27, COMPOUND_MACRO:3 | Algebra, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus |
| APPLY_THEOREM | 29 | APPLY_THEOREM | CORE_PROOF_OPERATION | ATOMIC:27, COMPOUND_MACRO:2 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus |
| MODULAR_REASONING | 26 | MODULAR_REASONING | DOMAIN_LIBRARY | ATOMIC:12, COMPOUND_MACRO:14 | Algebra, Counting & Probability, Intermediate Algebra, Number Theory, Prealgebra, Precalculus |
| VERIFY | 24 | VERIFY | CORE_PROOF_OPERATION | COMPOUND_MACRO:14, ATOMIC:10 | Algebra, Counting & Probability, Intermediate Algebra, Number Theory, Prealgebra, Precalculus |
| SEQUENCE_RECURRENCE | 23 | SEQUENCE_RECURRENCE | DOMAIN_LIBRARY | ATOMIC:19, COMPOUND_MACRO:4 | Algebra, Counting & Probability, Intermediate Algebra, Number Theory, Prealgebra, Precalculus |
| TRIG_IDENTITY | 23 | TRIG_IDENTITY | DOMAIN_LIBRARY | ATOMIC:22, COMPOUND_MACRO:1 | Intermediate Algebra, Precalculus |
| APPLY_DEFINITION | 19 | APPLY_DEFINITION | CORE_PROOF_OPERATION | COMPOUND_MACRO:3, ATOMIC:16 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Precalculus |
| OPTIMIZE | 17 | OPTIMIZE | CORE_PROOF_OPERATION | ATOMIC:13, COMPOUND_MACRO:4 | Algebra, Counting & Probability, Geometry, Number Theory, Prealgebra |
| CASE_SPLIT | 15 | CASE_SPLIT | CORE_PROOF_OPERATION | ATOMIC:15 | Algebra, Counting & Probability, Intermediate Algebra, Number Theory, Precalculus |
| COUNT | 12 | COUNT | DOMAIN_LIBRARY | ATOMIC:8, COMPOUND_MACRO:4 | Counting & Probability, Number Theory, Prealgebra, Precalculus |
| PROBABILITY | 12 | PROBABILITY | DOMAIN_LIBRARY | COMPOUND_MACRO:6, ATOMIC:6 | Counting & Probability, Geometry, Intermediate Algebra, Prealgebra |
| CONSTRUCT | 9 | CONSTRUCT | CORE_STATE_OPERATION | ATOMIC:9 | Algebra, Geometry, Intermediate Algebra, Number Theory, Prealgebra |
| INDUCT | 7 | INDUCT | CORE_PROOF_OPERATION | ATOMIC:6, COMPOUND_MACRO:1 | Algebra, Intermediate Algebra, Number Theory, Precalculus |
| SEARCH_META | 7 | SEARCH_META | SEARCH_META_OPERATION | ATOMIC:6, COMPOUND_MACRO:1 | Algebra, Counting & Probability, Geometry, Number Theory, Prealgebra |
| SUBSTITUTE | 7 | SUBSTITUTE | CORE_PROOF_OPERATION | ATOMIC:7 | Algebra, Intermediate Algebra, Number Theory, Precalculus |
| CONTRADICTION | 6 | CONTRADICTION | CORE_PROOF_OPERATION | COMPOUND_MACRO:1, ATOMIC:5 | Algebra, Intermediate Algebra, Number Theory, Precalculus |
| FORMULATE_EQUATION | 6 | MODEL | CORE_STATE_OPERATION | ATOMIC:5, COMPOUND_MACRO:1 | Algebra, Geometry, Prealgebra |
| SOLVE | 6 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:4, COMPOUND_MACRO:2 | Algebra, Intermediate Algebra, Precalculus |
| INTRODUCE_VARIABLE | 5 | DECLARE | CORE_STATE_OPERATION | ATOMIC:5 | Algebra, Geometry, Number Theory, Prealgebra |
| COUNT_CASES | 4 | UNRESOLVED | UNRESOLVED | ATOMIC:4 | Counting & Probability, Number Theory |
| EXPAND | 4 | TRANSFORM | SYMBOLIC_BACKEND_OPERATION | ATOMIC:4 | Algebra, Geometry, Intermediate Algebra, Precalculus |
| VERIFY_CANDIDATE | 4 | VERIFY | CORE_PROOF_OPERATION | ATOMIC:4 | Algebra, Number Theory, Prealgebra |
| COMBINE_CASE_COUNTS | 3 | COUNT | DOMAIN_LIBRARY | ATOMIC:3 | Counting & Probability, Number Theory |
| CONDITIONAL_PROBABILITY | 3 | EVALUATE | DOMAIN_LIBRARY | ATOMIC:3 | Counting & Probability |
| DISCHARGE_GOAL | 3 | DISCHARGE | CORE_PROOF_OPERATION | ATOMIC:3 | Algebra, Intermediate Algebra, Prealgebra |
| FACTOR | 3 | TRANSFORM | SYMBOLIC_BACKEND_OPERATION | ATOMIC:3 | Geometry, Intermediate Algebra |
| SELECT_CANDIDATE | 3 | SELECT | CORE_PROOF_OPERATION | ATOMIC:3 | Geometry, Number Theory |
| ADD_BOTH_SIDES | 2 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:2 | Algebra, Intermediate Algebra |
| APPLY_IDENTITY | 2 | APPLY_THEOREM | THEOREM_LIBRARY | ATOMIC:2 | Algebra, Precalculus |
| BOUND | 2 | BOUND | CORE_PROOF_OPERATION | ATOMIC:1, COMPOUND_MACRO:1 | Number Theory |
| BOUND_REASONING | 2 | BOUND | CORE_PROOF_OPERATION | ATOMIC:2 | Counting & Probability, Number Theory |
| BOUND_SEARCH | 2 | SEARCH_META | SEARCH_META_OPERATION | ATOMIC:2 | Number Theory |
| COMPLEMENT_COUNT | 2 | COUNT | DOMAIN_LIBRARY | ATOMIC:2 | Counting & Probability |
| COUNT_PERMUTATIONS | 2 | COUNT | DOMAIN_LIBRARY | ATOMIC:2 | Counting & Probability |
| ENUMERATE | 2 | ENUMERATE | SEARCH_META_OPERATION | ATOMIC:2 | Counting & Probability, Geometry |
| EVALUATE_PROBABILITY | 2 | EVALUATE | DOMAIN_LIBRARY | ATOMIC:2 | Counting & Probability |
| INCLUSION_EXCLUSION | 2 | INCLUSION_EXCLUSION | THEOREM_LIBRARY | ATOMIC:2 | Counting & Probability, Number Theory |
| SOLVE_CASE | 2 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:2 | Algebra |
| ADVANCE_SEQUENCE | 1 | TRANSFORM | DOMAIN_LIBRARY | ATOMIC:1 | Number Theory |
| APPLY_PRECEDENCE | 1 | APPLY_DEFINITION | CORE_PROOF_OPERATION | ATOMIC:1 | Prealgebra |
| CANCEL_SYMMETRIC_TERMS | 1 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:1 | Precalculus |
| CLEAR_DENOMINATOR | 1 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:1 | Precalculus |
| COMBINE_CASES | 1 | UNRESOLVED | UNRESOLVED | ATOMIC:1 | Precalculus |
| COMBINE_LIKE_TERMS | 1 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:1 | Intermediate Algebra |
| CONSTRAINT_PROPAGATION | 1 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:1 | Counting & Probability |
| COUNT_EXCLUDED | 1 | COUNT | DOMAIN_LIBRARY | ATOMIC:1 | Number Theory |
| CROSS_MULTIPLY | 1 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:1 | Algebra |
| DIFFERENTIATE | 1 | DIFFERENTIATE | DOMAIN_LIBRARY | ATOMIC:1 | Counting & Probability |
| DIVIDE_BOTH_SIDES | 1 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:1 | Algebra |
| EXTRACT_ROOT | 1 | TRANSFORM | CORE_PROOF_OPERATION | ATOMIC:1 | Algebra |
| FORMULATE_INEQUALITY | 1 | MODEL | CORE_STATE_OPERATION | ATOMIC:1 | Prealgebra |
| INDEX_TRANSLATION | 1 | TRANSFORM | DOMAIN_LIBRARY | ATOMIC:1 | Number Theory |
| MULTIPLY_CONDITIONALS | 1 | EVALUATE | DOMAIN_LIBRARY | ATOMIC:1 | Counting & Probability |
| MULTIPLY_COUNTS | 1 | COUNT | DOMAIN_LIBRARY | ATOMIC:1 | Counting & Probability |
| PARAMETERIZE_CONGRUENCE | 1 | TRANSFORM | DOMAIN_LIBRARY | ATOMIC:1 | Number Theory |
| PRIME_FACTORIZE | 1 | TRANSFORM | DOMAIN_LIBRARY | ATOMIC:1 | Number Theory |
| RATIONALIZE | 1 | TRANSFORM | SYMBOLIC_BACKEND_OPERATION | ATOMIC:1 | Precalculus |
| RECORD_EQUALITY_CONDITION | 1 | RECORD | CORE_PROOF_OPERATION | ATOMIC:1 | Intermediate Algebra |
| RECORD_GIVEN | 1 | RECORD | CORE_STATE_OPERATION | ATOMIC:1 | Algebra |
| ROUND_TO_DOMAIN | 1 | UNRESOLVED | UNRESOLVED | ATOMIC:1 | Prealgebra |
| SELECT_EXTREMUM | 1 | SELECT | CORE_PROOF_OPERATION | ATOMIC:1 | Algebra |
| SUBTRACT_BOTH_SIDES | 1 | TRANSFORM | CORE_PROOF_OPERATION | COMPOUND_MACRO:1 | Prealgebra |
| TAKE_LIMIT | 1 | TAKE_LIMIT | DOMAIN_LIBRARY | ATOMIC:1 | Algebra |

## Ontology boundary

Core candidates describe state/proof effects such as DECLARE, MODEL, TRANSFORM, SUBSTITUTE, CASE_SPLIT, VERIFY, SELECT, BOUND, CONSTRUCT, EVALUATE, and DISCHARGE. Theorem names, domain procedures, and symbolic/numeric computations remain library/backend evidence unless the trajectory changes generic proof state.

SEARCH_META is kept distinct from execution. The source can justify a representation choice or subgoal without exposing failed alternatives; those records should not be collapsed into ordinary TRANSFORM steps.
