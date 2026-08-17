# Structural Relation Coverage

This is a source/authority audit only. It does not add vocabulary or semantics.

| Concept | Classification | Evidence / limitation |
|---|---|---|
| `SOURCE` | `EXISTING_EXPLICIT` | source IDs, theorem, file, step, and revision |
| `TARGET` | `EXISTING_EXPLICIT` | explicit Lean goals |
| `VIA` | `EXISTING_EXPLICIT` | exact source tactic/action |
| `DERIVED_FROM` | `SOURCE_MISSING` | action premise lists are future/action-derived, not a state claim graph |
| `LEADS_TO` | `EXISTING_EXPLICIT` | ordered exact before/action/after traces |
| `ENTAILS` | `SOURCE_DERIVABLE_WITH_CURRENT_SEMANTICS` | individual verified Lean transitions; no general in-state relation graph |
| `EQUIVALENT_TO` | `SOURCE_MISSING` | not explicitly annotated as a state relation |
| `CONTRADICTS` | `SOURCE_MISSING` | conservative `P`/`¬P` case pairs are scoped alternatives, not a relation graph |
| `NECESSARY_FOR` | `SOURCE_MISSING` | no explicit state relation |
| `SUFFICIENT_FOR` | `SOURCE_MISSING` | no explicit state relation |
| `DEPENDS_ON` | `SOURCE_MISSING` | no claim-to-claim dependency graph |
| `SUPPORTS` | `SOURCE_MISSING` | no explicit state relation |
| `ENABLES` | `SOURCE_MISSING` | no explicit state relation |
| `REQUIRES` | `EXISTING_COMPOSITIONAL` | Lean local hypotheses constrain goals, but no exported obligation graph |
| `BLOCKS` | `SOURCE_MISSING` | no explicit state relation |
| `REWRITES_TO` | `SOURCE_DERIVABLE_WITH_CURRENT_SEMANTICS` | only where exact source tactic/transition demonstrates rewrite; not inferred lexically |
| `REDUCES_TO` | `SOURCE_DERIVABLE_WITH_CURRENT_SEMANTICS` | only from explicit transition evidence |
| `GENERALIZES` | `SOURCE_MISSING` | no explicit state relation |
| `SPECIALIZES` | `SOURCE_MISSING` | no explicit state relation |
| `UNDER_ASSUMPTION` | `EXISTING_EXPLICIT` | goal-local hypotheses and case scope |
| `VALID_ON` | `EXISTING_COMPOSITIONAL` | scope/local context supports locality, not branch coverage |
| `SUBGOAL_OF` | `SOURCE_DERIVABLE_WITH_CURRENT_SEMANTICS` | multi-goal transition ancestry is ordered but not exported as named relation edges |
| `DISCHARGES` | `SOURCE_DERIVABLE_WITH_CURRENT_SEMANTICS` | goal-count decrease is explicit; it is not an HML obligation discharge |

Current VNext can express richer branches, obligations, candidates, and scopes, but
language capability is not source annotation. Populating those fields without
source evidence would be fabrication.

