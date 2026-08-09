# MATH-GAP-0001: Explicit exhaustive case splitting and branch merge

- Classification: `CORE_REASONING_OPERATION`
- Mathematical operation: `CASE_SPLIT`

## Evidence in Gold-25

- `MATH-GOLD-004` `s1` — We can split the expression $|5x-1|=x+3$ into two separate cases.
- `MATH-GOLD-004` `s2` — 5x-1&=x+3
- `MATH-GOLD-004` `s4` — 5x-1&=-(x+3)
- `MATH-GOLD-007` `s5` — Therefore, either $y=-1$ and $x=y+4=3$, or $y=-3$ and $x=y+4=1$.
- `MATH-GOLD-007` `s6` — Either way, $xy = \boxed{-3}$.
- `MATH-GOLD-010` `s1` — There are two cases here: either Tom chooses two yellow marbles (1 result), or he chooses two marbles of different colors
- `MATH-GOLD-010` `s3` — The total number of distinct pairs of marbles Tom can choose is
- `MATH-GOLD-012` `s3` — There are two ways two dice add to 10: $4+6$ and $5+5$.
- `MATH-GOLD-012` `s8` — Adding the probabilities of these two cases gives us a total probability of $\frac{1}{72} + \frac{1}{72} = \boxed{\frac{1}{36}}$.
- `MATH-GOLD-019` `s4` — If $x = e^{\pi i/6}$, then
- `MATH-GOLD-019` `s5` — and if $x = e^{11 \pi i/6}$, then
- `MATH-GOLD-019` `s6` — In either case, $x^{18} = \boxed{-1}$.

## Expected mathematical semantics

Create branch-local assumptions, ensure branches are exhaustive/disjoint, and merge only facts valid in every branch.

## Current HML capability

HML has lexical scope blocks and scoped assumptions, but no case-split constructor, coverage proof, or branch-join rule.

## Exact failure point

The source has a finite or conditional partition, but current HML cannot establish coverage/disjointness or promote only branch-invariant facts after a join.

## Core/library/surface boundary

Core reasoning operation: branch-local scope is already a core concern, and coverage/join changes operational proof-state semantics rather than adding a theorem name.

## Smallest possible remedy

A generic case-analysis evidence object with predicates, coverage/disjointness proof references, branch scopes, and an invariant-only join.

## Semantic impact

Operational semantics and proof state; it changes which facts are globally established, not surface rendering.

## Dependencies on other gaps

Depends on existing lexical scope, proposition evaluation, and dependency/provenance edges; candidate verification often consumes its branch outputs.

## Risk of overfitting Gold-25

High if designed around absolute values or dice syntax; keep predicates and joins generic and library-neutral.

## Relevant inspected constructs

- `hml_core/src/hamiltonian_lang/ast/nodes.py`
- `hml_core/src/hamiltonian_lang/parser/__init__.py`
- `hml_core/src/hamiltonian_lang/reasoning/kernel.py`
- `hml_core/src/hamiltonian_lang/reasoning/check.py`
- `hml_core/src/hamiltonian_lang/reasoning/side_conditions.py`
- `hml_core/src/hamiltonian_lang/reasoning/certificates/builtin.py`
- `hml_core/src/hamiltonian_lang/verification/obligations/engine.py`

## Why the gap is not silently repaired

The canonical trajectory records the operation, warrant, preconditions, obligations, dependencies, and verification status independently of HML. The gap is reported rather than represented as a made-up HML rule.

## Proposed direction

Add a principled case-analysis/branch-merge semantic only if repeated evidence justifies it; do not add example-specific syntax.
