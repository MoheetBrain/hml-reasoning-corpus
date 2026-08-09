# MATH-GAP-0008: Counting and probability reasoning

- Classification: `DOMAIN_LIBRARY`
- Mathematical operation: `COMBINATORIAL_REASONING`

## Evidence in Gold-25

- `MATH-GOLD-010` `s1` — There are two cases here: either Tom chooses two yellow marbles (1 result), or he chooses two marbles of different colors
- `MATH-GOLD-010` `s2` — $\binom{4}{2}=6$ results
- `MATH-GOLD-010` `s3` — The total number of distinct pairs of marbles Tom can choose is
- `MATH-GOLD-011` `s1` — We can find the probability that no women are selected and subtract it from 1
- `MATH-GOLD-011` `s2` — the chance that the first person selected is male is $\frac{7}{10}$.
- `MATH-GOLD-011` `s3` — Then the probability that the second person selected is male is reduced to $\frac{6}{9}=\frac{2}{3}$.
- `MATH-GOLD-011` `s4` — For the third person, the probability is $\frac{5}{8}$.
- `MATH-GOLD-011` `s5` — So the probability that only men are selected is $$\frac{7}{10}\cdot\frac{2}{3}\cdot\frac{5}{8}=\frac{7}{24}.$$
- `MATH-GOLD-011` `s6` — Now we subtract from 1 to find the probability that at least one woman is selected. The probability is $1-\frac{7}{24}=\boxed{\frac{17}{24}}$.
- `MATH-GOLD-012` `s1` — At least one of the dice must come up 6, since otherwise the best we can do is 15.
- `MATH-GOLD-012` `s2` — The other two dice must add up to 10.
- `MATH-GOLD-012` `s3` — There are two ways two dice add to 10: $4+6$ and $5+5$.
- `MATH-GOLD-012` `s4` — A) The dice are 6, 6, 4.
- `MATH-GOLD-012` `s5` — There are three possible ways this can happen, and the probability of each is $(1/6)^3 = 1/216$.
- `MATH-GOLD-012` `s6` — B) The dice are 6, 5, 5.
- `MATH-GOLD-012` `s7` — So, the probability of this case is $3(1/216) = 1/72$.
- `MATH-GOLD-012` `s8` — Adding the probabilities of these two cases gives us a total probability of $\frac{1}{72} + \frac{1}{72} = \boxed{\frac{1}{36}}$.
- `MATH-GOLD-013` `s1` — In a four-digit palindrome, the first digit is the same as the last, and the second digit is the same as the third digit.
- `MATH-GOLD-013` `s2` — There are 9 options for the first/last digit (1 through 9 -- the first digit cannot be 0)
- `MATH-GOLD-013` `s3` — and there are 10 options for the second/third digit (0 through 9).
- `MATH-GOLD-013` `s4` — This gives us $9 \cdot 10 = \boxed{90}$ four-digit palindromes.
- `MATH-GOLD-017` `s4` — Therefore, in forming a perfect cube factor of 72

## Expected mathematical semantics

Finite sample spaces, case multiplicities, complements, conditional products, and product/sum rules are represented with exact counts and dependencies.

## Current HML capability

HML has probability types/expressions and generic state syntax, but no trusted combinatorial or probability rule set for these transitions.

## Exact failure point

Finite case counts, complements, conditional products, and permutation multiplicities are not checked by any current trusted HML rule despite exact numeric leaves being representable.

## Core/library/surface boundary

Domain library: sample-space semantics and counting laws are mathematical knowledge over generic state/claims.

## Smallest possible remedy

A finite counting/probability evidence package with explicit sample space, independence/sampling assumptions, and exact count certificates.

## Semantic impact

Denotation of probability/count claims and their epistemic verification; no new surface keyword is necessary.

## Dependencies on other gaps

Depends on finite-domain state, branch/case joins, exact arithmetic, and theorem-library evidence.

## Risk of overfitting Gold-25

High if shaped only around dice/marbles; specify abstract finite sets and measures.

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

Develop a finite-counting/probability library with explicit sample-space assumptions; do not add probability laws to the kernel.
