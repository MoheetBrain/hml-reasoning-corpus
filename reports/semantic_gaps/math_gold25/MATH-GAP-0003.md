# MATH-GAP-0003: Domain and applicability preconditions beyond current partiality

- Classification: `PRECONDITION_SYSTEM`
- Mathematical operation: `PRECONDITION_AUDIT`

## Evidence in Gold-25

- `MATH-GOLD-002` `s4` — Taking the square root of 144, we see that $x + y = \boxed{12}$.
- `MATH-GOLD-003` `s1` — Multiplying both sides by $x-5$ and by 3 gives $2(x-5) = 4(3)$.
- `MATH-GOLD-006` `s1` — to turn $\log_4 x$ into
- `MATH-GOLD-018` `s3` — = \frac{\sqrt{3} + 1}{\sqrt{3} - 1}
- `MATH-GOLD-019` `s1` — We can rewrite the given equation as $x^2 - \sqrt{3} x + 1 = 0$

## Expected mathematical semantics

Logarithm bases/arguments, radical domains, nonzero denominators, sign conditions, and theorem hypotheses remain explicit and dischargeable.

## Current HML capability

HML has require statements, term-level division partiality, and selected rule obligations, but no general domain-condition generator for logs, radicals, squaring, or theorem application.

## Exact failure point

The trajectory records a condition such as a positive log argument, nonzero denominator, or nonzero rationalizing factor, but current HML does not synthesize/check the domain predicate for the compound operation.

## Core/library/surface boundary

Precondition system: the missing item is applicability machinery, not a new mathematical theorem or surface keyword.

## Smallest possible remedy

A general applicability-obligation schema that lets a library theorem or operation declare domain predicates and discharge evidence.

## Semantic impact

Operational legality and proof state; typing may supply some predicates, while denotation remains unchanged.

## Dependencies on other gaps

Depends on type/refinement constraints, partiality checks, theorem-library hypotheses, and candidate verification.

## Risk of overfitting Gold-25

Moderate; define predicates compositionally instead of enumerating logs, radicals, and trigonometry separately.

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

Extend the obligation/precondition interface only after a recurring domain-condition vocabulary is empirically confirmed.
