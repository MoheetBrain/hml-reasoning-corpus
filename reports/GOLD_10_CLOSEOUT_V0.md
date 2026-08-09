# HML Reasoning Corpus V0 — Gold-10 closeout

## Problems chosen

1. G01 — simple equation isolation
2. G02 — multi-step algebraic substitution
3. G03 — function evaluation/dependency chain
4. G04 — inequality transformation with a positive multiplier precondition
5. G05 — direct logical implication
6. G06 — implication with an undetermined result
7. G07 — quantifier/binder reasoning
8. G08 — contrapositive reasoning
9. G09 — elementary probability/conditional reasoning
10. G10 — reciprocal derivative with an explicit nonzero precondition

## Results

- Canonical trajectories: **10**, all deterministically verified.
- Canonical reasoning transitions: **23**.
- HML renderings: all 10 parse/type-check at the pinned HML SHA.
- HML fully verifies the local reasoning spine in G04, G05, and G08; other renderings
  intentionally expose open or uncomputed portions instead of claiming more than HML proves.
- Semantic gaps: **6 distinct reports**, affecting 12 transition references.
- CoreGapRate: **3 / 23 = 13.04%**.
- Library-gap rate: **8 / 23 = 34.78%**.
- Minor-surface-gap rate: **0 / 23 = 0.00%**.
- Ambiguous/human-implicit rate: **1 / 23 = 4.35%**.

The complete operation matrix is in [REASONING_COVERAGE_V0.md](REASONING_COVERAGE_V0.md),
and the exact payload size is in [GOLD_10_SIZE.md](GOLD_10_SIZE.md).

## What worked well in current HML

Typed declarations and domains, explicit assumptions, the v2 `goal`/`derive`/`proved`
spine, equality and inequality kernels, generated side-condition obligations, modus
ponens, modus tollens, binder parsing/scope, conditional-probability representation, and
derivative precondition representation all worked as useful structural building blocks.

## Hardest recurring concepts

Arithmetic normalization, executable definition/dependency evaluation, explicit
undetermined epistemic outcomes, quantified theorem discharge, probability identities, and
calculus rule execution remain outside the faithfully certified HML surface.

## Schema decision

The canonical trajectory schema is sufficient for Gold-10: it records state content,
actions, dependencies, provenance, verification, epistemic status, and support classes.
No blocking schema revision is required before stopping. A future revision should make
countermodel evidence and non-entailment a typed evidence variant rather than only a claim
string.

## Verifier coverage

The standard-library test suite validates trajectory shape, state/action reference
resolution, action provenance, all 16 reasoning-stage IDs, semantic-gap disclosure, HML
SHA headers, HML compilation, canonical arithmetic/logic/probability/calculus oracles, and
the frozen submodule guard. No MATH, AMPS, NuminaMath, or other large dataset was ingested.

## Recommendation

**STOP after Gold-10.** Do not proceed to Gold-100 automatically. Review the six semantic
gaps with the Hamiltonian Lang project and decide whether they are library work or genuine
core-semantic changes before expanding the corpus.
