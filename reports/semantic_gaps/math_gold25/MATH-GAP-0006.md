# MATH-GAP-0006: Open symbolic algebra normalization

- Classification: `LIBRARY_THEOREM`
- Mathematical operation: `SYMBOLIC_REWRITE`

## Evidence in Gold-25

- `MATH-GOLD-001` `s3` — This implies $a(2)+3=2-5$, which we solve to get $2a=-6 \Rightarrow a=-3$.
- `MATH-GOLD-001` `s5` — Substituting, we get $-2-5=2(-2)-b$, which implies $b=3$.
- `MATH-GOLD-001` `s6` — So $a+b=-3+3=\boxed{0}$.
- `MATH-GOLD-002` `s3` — Note that $(x + y)^2 = x^2 + y^2 + 2xy = 90 + 2\cdot 27 = 144$.
- `MATH-GOLD-002` `s4` — Taking the square root of 144, we see that $x + y = \boxed{12}$.
- `MATH-GOLD-003` `s2` — Expanding the left side gives $2x-10 = 12$.
- `MATH-GOLD-007` `s3` — 12y^2 + 48y + 36 = 0.
- `MATH-GOLD-007` `s4` — Thus, $y^2 + 4y + 3 = 0$, so $(y+1)(y+3) = 0$.
- `MATH-GOLD-015` `s5` — Then $n\ge 6\implies a=4+5n\ge 34$.
- `MATH-GOLD-018` `s3` — = \frac{\sqrt{3} + 1}{\sqrt{3} - 1}
- `MATH-GOLD-018` `s4` — = \frac{3 + 2 \sqrt{3} + 1}{2}
- `MATH-GOLD-021` `s3` — Expanding $(x + 1)^2$, we get
- `MATH-GOLD-021` `s4` — This can be simplified to $2x^2 + 2x = 840$, or $x^2 + x = 420$.
- `MATH-GOLD-022` `s2` — Thus, we have \begin{align*}
- `MATH-GOLD-022` `s3` — We want to find two integers whose product is 80, such that one integer is two more than the other.
- `MATH-GOLD-022` `s4` — We note that 80 can be factored as $8\cdot 10$. Therefore, $r = \boxed{8}$.
- `MATH-GOLD-024` `s1` — When solving this problem, we must remember to apply the order of operations.
- `MATH-GOLD-025` `s4` — We therefore have the inequality

## Expected mathematical semantics

Expansion, factoring, collection, radical normalization, and sign-directed algebraic equivalence are justified over variables.

## Current HML capability

HML's trusted kernel is structural and local; the symbolic equivalence checker is explicitly untrusted, while exact evaluation only handles closed claims.

## Exact failure point

Open-variable expansion, factoring, collection, radical normalization, or monotonicity cannot be certified by the trusted closed evaluator; the symbolic-equivalence checker is not trusted.

## Core/library/surface boundary

Library/verifier boundary: generic equality reasoning is core, while certified normalization/search is a reusable algebra library or checker.

## Smallest possible remedy

A replayable symbolic-algebra proof object or certified normal-form checker exposed through evidence.

## Semantic impact

Denotation and verification of open expressions; no new surface syntax is inherently required.

## Dependencies on other gaps

Depends on typed expression normalization, domain conditions, and exact arithmetic leaves.

## Risk of overfitting Gold-25

High if rewrite rules are added one by one for Gold-25 identities; use a general certified algebra backend.

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

Use replayable certified algebra evidence or a library proof object; do not add rewrite rules for the 25 examples.
