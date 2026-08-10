# Core operation adjudication v1

These are derived-view decisions. Frozen observed labels are unchanged.

| Operation | Frequency | Domains | Layer evidence | Decision | Evidence |
|---|---:|---|---|---|---|
| TRANSFORM | 305 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus | {'CORE': 221, 'THEOREM_LIBRARY': 2, 'SYMBOLIC_BACKEND': 9, 'DOMAIN_LIBRARY': 73} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| UNRESOLVED | 136 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus | {'CORE': 7, 'UNKNOWN': 125, 'SEARCH_META': 4} | UNRESOLVED | Insufficient source evidence or explicitly ambiguous OTHER/search text. |
| DISCHARGE | 90 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus | {'CORE': 90} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| EVALUATE | 50 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus | {'NUMERIC_BACKEND': 31, 'CORE': 6, 'DOMAIN_LIBRARY': 13} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| APPLY_THEOREM | 29 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus | {'THEOREM_LIBRARY': 29} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| VERIFY | 28 | Algebra, Counting & Probability, Intermediate Algebra, Number Theory, Prealgebra, Precalculus | {'CORE': 28} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| BOUND | 23 | Algebra, Counting & Probability, Geometry, Number Theory, Prealgebra | {'CORE': 23} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| COUNT | 23 | Counting & Probability, Number Theory, Prealgebra, Precalculus | {'CORE': 21, 'THEOREM_LIBRARY': 2} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| APPLY_DEFINITION | 19 | Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Precalculus | {'CORE': 19} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| CASE_SPLIT | 15 | Algebra, Counting & Probability, Intermediate Algebra, Number Theory, Precalculus | {'CORE': 15} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| CONSTRUCT | 12 | Algebra, Geometry, Intermediate Algebra, Number Theory, Prealgebra | {'CORE': 9, 'SEARCH_META': 3} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| INDUCT | 7 | Algebra, Intermediate Algebra, Number Theory, Precalculus | {'CORE': 7} | MERGE_INTO_OTHER_CORE | No independent evidence supports a distinct primitive. |
| MODEL | 7 | Algebra, Geometry, Prealgebra | {'CORE': 7} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| SUBSTITUTE | 7 | Algebra, Intermediate Algebra, Number Theory, Precalculus | {'CORE': 7} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| CONTRADICTION | 6 | Algebra, Intermediate Algebra, Number Theory, Precalculus | {'CORE': 6} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| DECLARE | 5 | Algebra, Geometry, Number Theory, Prealgebra | {'CORE': 5} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| SELECT | 4 | Algebra, Geometry, Number Theory | {'CORE': 4} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| ENUMERATE | 2 | Counting & Probability, Geometry | {'CORE': 2} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |
| RECORD | 1 | Algebra | {'CORE': 1} | KEEP_AS_CORE | Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes. |

## Specific cleanup decisions

- TRIG_IDENTITY -> TRANSFORM plus TRIGONOMETRY_IDENTITY warrant and DOMAIN_LIBRARY.
- MODULAR_REASONING -> TRANSFORM plus MODULAR_ARITHMETIC warrant and DOMAIN_LIBRARY.
- PROBABILITY/EVALUATE_PROBABILITY -> EVALUATE plus PROBABILITY_LAW warrant and DOMAIN_LIBRARY.
- SEQUENCE_RECURRENCE -> TRANSFORM plus SEQUENCE_RULE warrant and DOMAIN_LIBRARY.
- DIFFERENTIATE/INTEGRATE -> TRANSFORM plus CALCULUS_RULE warrant and DOMAIN_LIBRARY.
- TAKE_LIMIT -> EVALUATE plus CALCULUS_RULE warrant and DOMAIN_LIBRARY.
- INCLUSION_EXCLUSION/PIGEONHOLE -> COUNT plus theorem/counting warrant.
- OPTIMIZE -> BOUND with goal_effect=ADVANCE.
- DISCHARGE -> goal effect, with an underlying operation retained when evidenced.
- OTHER and unsupported search/meta choices remain UNRESOLVED.
