# Empirical reasoning-state profile v0

This profile is derived from the 25 audited MATH trajectories, not from intuition. The
sample contains 118 canonical transitions across seven MATH categories.

## 1. Necessary-looking S_t information

| State component | Evidence |
|---|---:|
| Objects/declarations | 25/25 trajectories |
| Types/domains | 25/25 trajectories |
| Active facts/constraints | 25/25 trajectories |
| Explicit goal | 25/25 trajectories |
| Dependencies/provenance | 99/118 transitions cite prior facts or results |
| Scope/branch context | 3/25 trajectories contain branch-local reasoning |
| Preconditions | 25/118 transitions record at least one |
| Obligations | 6/118 transitions create explicit debt |

The evidence supports a state containing typed objects, active facts/constraints, goals,
dependency edges, and a scope context. These are not interchangeable: a theorem
hypothesis may be a fact, a branch assumption, or an obligation depending on how it was
introduced.

## 2. Useful but not universal

- Definitions/functions are essential in the function/parity and formula examples but
  absent from direct arithmetic/counting problems.
- Branch sets are essential for absolute values, roots, complex candidates, and finite
  cases, but not for direct transformations.
- Explicit epistemic status is useful when a step is only conditionally supported or
  when a candidate has been generated but not checked.
- Exact backend evidence is useful for arithmetic leaves, but it does not replace the
  theorem/library warrant that produced the expression.

## 3. What can live outside the core state

Surface prose, source sentence boundaries, textbook discourse markers, and rendering
syntax can live in provenance/views. The theorem name and proof object can be library
artifacts referenced by a generic `APPLY_THEOREM` action. Numeric backend traces can be
verification evidence, not canonical state facts, provided their dependency claims are
retained.

## 4. Are facts enough?

No. Dependencies are structurally important: the same expression has different semantic
status when it is given, derived by a checked rule, produced in a branch, or returned by
an untrusted oracle. The Gold-25 trajectory keeps dependencies on every transition.

## 5. Goals

Goals are explicit in all 25 selected problems because selection deliberately targeted
complete worked answers. This is a selection property, not an estimate for all prose.
Within a trajectory, subgoals/candidate goals appear when solving, branching, or
constructing witnesses.

## 6. Preconditions

Preconditions are material in 25 of 118
steps. The most common are nonzero denominators, positive/log domains, sign conditions,
integer domains, theorem hypotheses, and branch predicates. Several source solutions
omit them; the reconstruction marks those omissions.

## 7. Obligations

The explicit reconstruction creates 6 obligations and discharges
6. The small count is misleading:
many obligations are hidden in textbook prose (candidate checking, radical sign,
branch coverage, theorem hypotheses). This is precisely why obligation state should not
be inferred from whether the final numeric answer looks plausible.

## 8. Scope and branches

Branch/scope structure matters in 3/25 trajectories. The current HML lexical
scope is a promising primitive, but case coverage and branch joins are not yet encoded.
Facts from one branch must not be promoted to global state without a merge argument.

## 9. Stored mathematical knowledge

Most nontrivial domain work invokes stored knowledge: AM-GM, Pythagorean theorem,
trigonometric identities, parity definitions, divisibility rules, prime factorization,
triangle inequality, finite probability rules, and congruence reasoning. This strongly
supports a small generic operation kernel plus explicit theorem/domain libraries.

## 10. Assessment of current HML

The HML semantic model is approximately right for local checked transitions: typed
claims, explicit goals, rule applications, obligations, scope, and provenance match the
observed shape. It is underpowered at reusable evidence for open symbolic/domain claims,
candidate/branch interfaces, and sequence/finite-search state. The data does not justify
adding textbook theorem names as core keywords.
