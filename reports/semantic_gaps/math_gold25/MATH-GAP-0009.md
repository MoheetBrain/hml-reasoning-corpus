# MATH-GAP-0009: Number-theory constraints and finite search

- Classification: `DOMAIN_LIBRARY`
- Mathematical operation: `NUMBER_THEORY`

## Evidence in Gold-25

- `MATH-GOLD-014` `s1` — We know that the prime factorization of 18 is $2\cdot 3^2$, so in order for the four digit number to be divisible by 18 it must also be divisible by 9 and 2.
- `MATH-GOLD-014` `s2` — In order for a number to be divisible by 9, the sum of its digits must be divisible by 9 as well.
- `MATH-GOLD-014` `s3` — Thus, $3+7+4+n$, or $14+n$, must be divisible by 9.
- `MATH-GOLD-014` `s4` — Since 18 is the smallest multiple of 9 that is greater than 10, $14+n=18$, and $n=18-14=\boxed{4}$.
- `MATH-GOLD-015` `s2` — The first congruence means that there exists a non-negative integer $n$ such that $a=4+5n$.
- `MATH-GOLD-015` `s3` — Substituting this into the second congruence yields \[4+5n\equiv 6\pmod 7\implies n\equiv 6\pmod 7\]
- `MATH-GOLD-015` `s4` — So $n$ has a lower bound of $6$.
- `MATH-GOLD-015` `s6` — $\boxed{34}$ is the smallest solution since it is a lower bound of $a$ and satisfies both original congruences.
- `MATH-GOLD-017` `s1` — Prime factorize $72$ as $2^3\cdot 3^2$.
- `MATH-GOLD-017` `s2` — A positive integer is a factor of 72 if and only if the exponents in its prime factorization are less than or equal to the corresponding exponents in the prime factorization of 72.
- `MATH-GOLD-017` `s3` — Also, a positive integer is a perfect cube if and only if every exponent is a multiple of 3.
- `MATH-GOLD-017` `s4` — Therefore, in forming a perfect cube factor of 72
- `MATH-GOLD-017` `s5` — There are $2\cdot 1=\boxed{2}$ ways to make these choices.
- `MATH-GOLD-021` `s5` — Indeed, $20 \times 21 = 420$, so the legs must be 20 and 21.
- `MATH-GOLD-022` `s3` — We want to find two integers whose product is 80, such that one integer is two more than the other.

## Expected mathematical semantics

Prime factorization, congruence solving, digit rules, divisor predicates, and finite minimality checks are certified.

## Current HML capability

Natural/integer types are present, but no trusted number-theory theorem or finite-search certificate interface exists.

## Exact failure point

Prime factorization, congruence parameterization, divisibility rules, and finite factor searches require trusted number-theoretic facts and minimality certificates absent from current HML.

## Core/library/surface boundary

Domain library: the generic operations are parameterize, constrain, enumerate, and verify; the number-theory facts are external knowledge.

## Smallest possible remedy

An audited number-theory library with factorization/congruence evidence and finite-search/minimality certificates.

## Semantic impact

Denotation and verification of integer claims; generic operational semantics can remain unchanged.

## Dependencies on other gaps

Depends on natural/integer typing, finite search state, candidate verification, and exact arithmetic.

## Risk of overfitting Gold-25

High if the API hard-codes digit-sum or cube-factor examples; keep predicates and certificates abstract.

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

Add audited number-theory evidence as a library capability.
