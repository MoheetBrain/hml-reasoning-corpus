# Stage 100 audit

## Result

**All 100 minimal pairs pass the mechanical contract, but only 20 pass the hard-negative
review. Decision: `FIX_GENERATOR_FIRST`.**

| Measure | Result |
|---|---:|
| attempted mutations | 100 |
| accepted pairs | 100 |
| semantic hard pairs | 20 |
| structural pairs | 60 |
| ambiguous pairs | 20 |
| trivial parser pairs | 0 |
| unknown/unsupported | 0 |
| valid alternatives | 0 |
| invalid counterfactuals | 100 |
| duplicate rate | 0.00% |
| source-record diversity | 100 |
| source-theorem/row diversity | 100 |
| provenance completeness | 100/100 |
| changed semantic fields | exactly 1 for every pair |
| dataset SHA-256 | `75519e5f45d76ed2db81c657c4467739f98d69ef9d29ffdcfa3958ff4f435e3f` |
| generator source SHA-256 | `4b0fa1332c39bd6220ce6720ad3cfe5dc891ae20a0befcf4e194eb2e58ab088d` |

Every source transition independently returns `VALID` from frozen HML. Every mutated
transition imports successfully and returns `INVALID` at the intended replay invariant.
No `UNRESOLVED` result was converted to `INVALID`; no syntax corruption was generated.

## Mutation-family distribution

| Family | Pairs |
|---|---:|
| `BRANCH_JOIN` | 10 |
| `CANDIDATES` | 10 |
| `DEPENDENCY` | 10 |
| `EPISTEMIC_STATUS` | 10 |
| `GOAL_DISCHARGE` | 10 |
| `OBLIGATIONS` | 10 |
| `PRECONDITIONS` | 10 |
| `SCOPE` | 10 |
| `TYPE_DOMAIN` | 10 |
| `WARRANT` | 10 |

## Failure-code distribution

| Verifier failure code | Count |
|---|---:|
| `CANDIDATE_PROMOTION` | 10 |
| `DEPENDENCY_VIOLATION` | 10 |
| `EPISTEMIC_PROMOTION` | 10 |
| `FALSE_GOAL_DISCHARGE` | 10 |
| `INVALID_BRANCH_JOIN` | 10 |
| `OBLIGATION_DROP` | 10 |
| `PRECONDITION_VIOLATION` | 10 |
| `SCOPE_LEAK` | 10 |
| `TYPE_OR_DOMAIN_MISMATCH` | 10 |
| `WARRANT_MISMATCH` | 10 |

## Causal interpretation

Each pair changes one verifier-semantic leaf: premise identity, scope, precondition
status, obligation materialisation, candidate constraint coverage, branch coverage,
evidence identity, epistemic evidence, goal status, or input domain. The source and
counterfactual both parse and import, so none is parser garbage. Independent review
nevertheless classifies missing sentinel IDs and direct status/effect contradictions as
`STRUCTURAL_PAIR`, not mathematically hard negatives. Scope and type mutations are
`AMBIGUOUS` because a second frame finding accompanies the target finding. Only the
candidate-constraint and branch-coverage mutations are retained as
`SEMANTIC_HARD_PAIR` at this checkpoint.

The primary verdict uses `OFFLINE_REPLAY` because the retained evidence bytes are from
the frozen externally adjudicated corpus. Runtime-without-attestation diagnostics are
recorded separately and are never treated as positive labels.

## Why Stage 1,000 is not authorized

The scale artifact is available and correctly pinned, but its Lean effect-first records
are not HML `Transition` payloads. `premises_used` is empty throughout the canonical
JSONL; preconditions, obligations, scopes, typed action arguments and evidence envelopes
are absent. Its `frozen_hml_representable=true` flag was assigned after excluding only
goal creation and is not a verifier replay result. Scaling now would either duplicate
these 100 fixture shapes or invent missing semantics.
