# Reasoning Coverage V0 — Gold-10

This is a diagnostic coverage report, not a statistical claim. The denominator is the
23 explicitly recorded canonical reasoning actions across the ten hand-authored examples.
The canonical trajectory remains the source of truth; HML is evaluated as a rendering.

| reasoning_operation | examples_seen | domains_seen | current_HML_support | semantic_gap_ids | verification_method |
|---|---|---|---|---|---|
| substitution | G02, G03 | algebra, functions | HML `substitute` verifies structural substitution; execution of dependent values needs a library | GAP-0002 | HML kernel plus exact substitution oracle |
| rewrite | G01, G02 | algebra | Equality-preserving rewrite is expressible; numeric normalization is not | GAP-0001 | HML kernel plus exact arithmetic |
| simplification | G01, G02, G09, G10 | algebra, probability, calculus | No current arithmetic normalizer | GAP-0001 | exact integer/decimal/rational oracles |
| equality-preserving transform | G01 | algebra | `subtract_both_sides` is VERIFIED | — | HML reasoning kernel |
| inequality transform | G04 | algebra | `multiply_inequality` is VERIFIED when `k > 0` is discharged | — | HML reasoning kernel plus literal-order oracle |
| dependency | G02, G03 | algebra, functions | Dependency structure is representable; executable evaluation is library-backed | GAP-0002 | dependency trace plus exact evaluation |
| subgoal | G03, G04, G07 | functions, algebra, quantifiers | State-level subgoals are canonical; HML does not uniformly certify them | GAP-0004 | trajectory reference checks and domain-specific oracle |
| implication | G05, G06, G08 | propositional logic | Modus ponens is VERIFIED; non-entailment is not a first-class HML outcome | GAP-0003 | complete Boolean truth table |
| negation | G06, G08 | propositional logic | `not` and modus tollens are expressible; epistemic refutation status is not | GAP-0003 | complete Boolean truth table |
| underdetermination | G06 | propositional logic | HML leaves an open goal rather than recording `undetermined` | GAP-0003 | countermodel plus entailment/refutation checks |
| quantifier | G07 | arithmetic, logic | Typed quantifier and alpha-scope parse; quantified proof discharge does not | GAP-0004 | symbolic identity oracle |
| scope | G07 | arithmetic, logic | Binder scope is expressible and checked | — | HML parser/scope representation |
| temporary assumption | G04 | algebra | Positive multiplier assumption discharges a generated HML obligation | — | HML obligation checker |
| contradiction/contrapositive | G08 | propositional logic | Contrapositive via modus tollens is VERIFIED | — | HML reasoning kernel plus truth table |
| precondition | G04, G09, G10 | algebra, probability, calculus | Explicit numeric/domain preconditions are representable; probability/calculus rule use is incomplete | GAP-0005, GAP-0006 | literal/domain oracles |
| theorem/rule application | G04, G05, G07, G08, G09, G10 | algebra, logic, probability, calculus | Closed HML rule catalogue covers several local rules; coverage is incomplete | GAP-0004, GAP-0005, GAP-0006 | HML kernel or domain-specific oracle |
| probability conditioning | G09 | probability | Conditional probability syntax and typing work; product inference is absent | GAP-0005 | conditional-probability identity |
| goal discharge | G01–G10 | all five domains | Canonical goal status is explicit; HML fully discharges G04, G05, and G08, while other renderings expose open/uncomputed work | GAP-0001–GAP-0006 | trajectory verifier plus HML check |

## Support classification counts

| classification | steps | rate |
|---|---:|---:|
| `EXPRESSIBLE_CURRENT_HML` | 11 | 47.83% |
| `EXPRESSIBLE_WITH_LIBRARY` | 8 | 34.78% |
| `REQUIRES_MINOR_SURFACE_EXTENSION` | 0 | 0.00% |
| `REQUIRES_NEW_CORE_SEMANTIC` | 3 | 13.04% |
| `AMBIGUOUS_OR_HUMAN_IMPLICIT` | 1 | 4.35% |
| `NOT_MACHINE_VERIFIABLE` | 0 | 0.00% |
| **total** | **23** | **100.00%** |

## CoreGapRate

`CoreGapRate = 3 / 23 = 0.1304347826` (13.04%).

The separate library-gap rate is `8 / 23 = 0.3478260870` (34.78%). The minor-surface-gap
rate is `0 / 23 = 0.0000000000` (0.00%). The ambiguous/human-implicit rate is
`1 / 23 = 0.0434782609` (4.35%). These rates are diagnostic only because the corpus has
ten examples and was selected for primitive coverage rather than sampling.
