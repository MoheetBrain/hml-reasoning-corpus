# MATH-GAP-0007: Mathematical domain libraries for logs, trig, vectors, parity, optimization, and complex numbers

- Classification: `DOMAIN_LIBRARY`
- Mathematical operation: `DOMAIN_REASONING`

## Evidence in Gold-25

- `MATH-GOLD-006` `s1` — to turn $\log_4 x$ into
- `MATH-GOLD-006` `s2` — That means that $\frac{3}{2}\log_2 x=6.
- `MATH-GOLD-006` `s3` — Dividing each side by $\frac{3}{2},
- `MATH-GOLD-007` `s5` — Therefore, either $y=-1$ and $x=y+4=3$, or $y=-3$ and $x=y+4=1$.
- `MATH-GOLD-008` `s1` — Substituting $-x$ for $x$ gives us $f(g(-x^3)) = f(-g(x^3)) = f(g(x^3))$
- `MATH-GOLD-008` `s2` — so $f(g(x^3))$ is $\boxed{\text{even}}$.
- `MATH-GOLD-009` `s1` — By AM-GM,
- `MATH-GOLD-009` `s2` — = 3 \sqrt[3]{8xyz} = 3 \sqrt[3]{8 \cdot 8} = 12.
- `MATH-GOLD-009` `s3` — Equality occurs when $x = 2y = 4z$ and $xyz = 8.$
- `MATH-GOLD-009` `s4` — We can solve to get $x = 4,$ $y = 2,$ and $z = 1,
- `MATH-GOLD-018` `s1` — From the angle addition formula,
- `MATH-GOLD-018` `s2` — = \frac{1 + \frac{1}{\sqrt{3}}}{1 - \frac{1}{\sqrt{3}}}
- `MATH-GOLD-019` `s1` — We can rewrite the given equation as $x^2 - \sqrt{3} x + 1 = 0$
- `MATH-GOLD-019` `s2` — so by the quadratic formula,
- `MATH-GOLD-019` `s3` — which means $x = e^{\pi i/6}$ or $x = e^{11 \pi i/6}$.
- `MATH-GOLD-019` `s4` — If $x = e^{\pi i/6}$, then
- `MATH-GOLD-019` `s5` — and if $x = e^{11 \pi i/6}$, then
- `MATH-GOLD-019` `s6` — In either case, $x^{18} = \boxed{-1}$.
- `MATH-GOLD-020` `s1` — Expanding the dot product, we get
- `MATH-GOLD-020` `s2` — = \mathbf{a} \cdot \mathbf{a} - \mathbf{b} \cdot \mathbf{b}
- `MATH-GOLD-020` `s3` — = \|\mathbf{a}\|^2 - \|\mathbf{b}\|^2
- `MATH-GOLD-020` `s4` — = 3^2 - 6^2 = \boxed{-27}.
- `MATH-GOLD-021` `s2` — Using the Pythagorean Theorem, we write the equation $x^2 + (x + 1)^2 = 29^2$
- `MATH-GOLD-022` `s1` — If $r$ is the radius of the circle, we know that $x = \pi r^2$ and $y = 2\pi r$.
- `MATH-GOLD-023` `s1` — Using the Triangle Inequality

## Expected mathematical semantics

Domain-specific facts and theorem hypotheses are imported as checked knowledge while generic operations remain small.

## Current HML capability

The HML type system represents several domains, but the reasoning kernel has no log/trig/vector/AM-GM/complex theorem rules.

## Exact failure point

The type system can represent logs, vectors, functions, complex values, and propositions, but current trusted rules do not establish their domain-specific identities.

## Core/library/surface boundary

Domain library: the observed operations share generic APPLY_DEFINITION/APPLY_THEOREM/VERIFY shapes and do not justify core keywords.

## Smallest possible remedy

Separate audited libraries for recurring domains, each returning explicit theorem/definition evidence and hypotheses.

## Semantic impact

Mostly denotation-level theorem availability and verifier epistemics; the generic core operational semantics need not change.

## Dependencies on other gaps

Depends on the theorem evidence interface, applicability obligations, and typed domain representations.

## Risk of overfitting Gold-25

Very high across only 25 examples; wait for cross-domain recurrence before freezing library APIs.

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

Separate domain libraries from core semantics and require explicit, replayable evidence.
