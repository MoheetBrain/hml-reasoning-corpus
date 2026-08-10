# Gold-125 operation long-tail analysis

36 observed source-granularity operation labels occur once or twice across the 125-trajectory corpus. A singleton label is not treated as a new core primitive merely because it has a distinct name.

| Observed operation | Frequency | Candidate core | Layer | Likelihood of genuine core primitive | Reason |
|---|---:|---|---|---|---|
| APPLY_PRECEDENCE | 1 | APPLY_DEFINITION | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| CANCEL_SYMMETRIC_TERMS | 1 | TRANSFORM | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| CLEAR_DENOMINATOR | 1 | TRANSFORM | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| COMBINE_LIKE_TERMS | 1 | TRANSFORM | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| CONSTRAINT_PROPAGATION | 1 | TRANSFORM | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| CROSS_MULTIPLY | 1 | TRANSFORM | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| DIVIDE_BOTH_SIDES | 1 | TRANSFORM | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| EXTRACT_ROOT | 1 | TRANSFORM | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| FORMULATE_INEQUALITY | 1 | MODEL | CORE_STATE_OPERATION | LOW | single-domain evidence only |
| RECORD_EQUALITY_CONDITION | 1 | RECORD | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| RECORD_GIVEN | 1 | RECORD | CORE_STATE_OPERATION | LOW | single-domain evidence only |
| SELECT_EXTREMUM | 1 | SELECT | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| SUBTRACT_BOTH_SIDES | 1 | TRANSFORM | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| ADD_BOTH_SIDES | 2 | TRANSFORM | CORE_PROOF_OPERATION | MEDIUM | generic candidate appears across domains but recurrence is still small |
| BOUND | 2 | BOUND | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| BOUND_REASONING | 2 | BOUND | CORE_PROOF_OPERATION | MEDIUM | generic candidate appears across domains but recurrence is still small |
| SOLVE_CASE | 2 | TRANSFORM | CORE_PROOF_OPERATION | LOW | single-domain evidence only |
| ADVANCE_SEQUENCE | 1 | TRANSFORM | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| COMBINE_CASES | 1 | UNRESOLVED | UNRESOLVED | INCONCLUSIVE | search/meta or unresolved representation choice |
| COUNT_EXCLUDED | 1 | COUNT | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| DIFFERENTIATE | 1 | DIFFERENTIATE | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| INDEX_TRANSLATION | 1 | TRANSFORM | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| MULTIPLY_CONDITIONALS | 1 | EVALUATE | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| MULTIPLY_COUNTS | 1 | COUNT | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| PARAMETERIZE_CONGRUENCE | 1 | TRANSFORM | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| PRIME_FACTORIZE | 1 | TRANSFORM | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| RATIONALIZE | 1 | TRANSFORM | SYMBOLIC_BACKEND_OPERATION | LOW | domain theorem, library, or backend procedure |
| ROUND_TO_DOMAIN | 1 | UNRESOLVED | UNRESOLVED | INCONCLUSIVE | search/meta or unresolved representation choice |
| TAKE_LIMIT | 1 | TAKE_LIMIT | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| APPLY_IDENTITY | 2 | APPLY_THEOREM | THEOREM_LIBRARY | LOW | domain theorem, library, or backend procedure |
| BOUND_SEARCH | 2 | SEARCH_META | SEARCH_META_OPERATION | INCONCLUSIVE | search/meta or unresolved representation choice |
| COMPLEMENT_COUNT | 2 | COUNT | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| COUNT_PERMUTATIONS | 2 | COUNT | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| ENUMERATE | 2 | ENUMERATE | SEARCH_META_OPERATION | MEDIUM | generic candidate appears across domains but recurrence is still small |
| EVALUATE_PROBABILITY | 2 | EVALUATE | DOMAIN_LIBRARY | LOW | domain theorem, library, or backend procedure |
| INCLUSION_EXCLUSION | 2 | INCLUSION_EXCLUSION | THEOREM_LIBRARY | LOW | domain theorem, library, or backend procedure |

The strongest evidence for a compact core is that many labels collapse into DECLARE, MODEL, TRANSFORM, SUBSTITUTE, APPLY_DEFINITION, APPLY_THEOREM, CASE_SPLIT, ENUMERATE, VERIFY, SELECT, BOUND, CONSTRUCT, EVALUATE, and DISCHARGE. The strongest threat is SEARCH_META: source-supported representation choices recur, but their successful paths do not expose the unchosen search tree.
