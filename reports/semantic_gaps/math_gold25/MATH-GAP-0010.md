# MATH-GAP-0010: Sequence indexing, exclusions, and discrete minimality

- Classification: `CORE_STATE_REPRESENTATION`
- Mathematical operation: `SEQUENCE_REASONING`

## Evidence in Gold-25

- `MATH-GOLD-016` `s1` — When 200 is reached in the sequence of non-square positive integers, all the perfect squares from $1^2$ up to $14^2$ have been omitted.
- `MATH-GOLD-016` `s2` — Therefore, 200 is the 186th term.
- `MATH-GOLD-016` `s3` — The 187th term is 201
- `MATH-GOLD-023` `s2` — so $n$ can be any integer from $5$ to $13,$ inclusive.
- `MATH-GOLD-023` `s3` — The sum can be calculated in several ways, but regardless
- `MATH-GOLD-025` `s5` — The smallest integer $x$ such that $400 < x$ is $401$.
- `MATH-GOLD-025` `s6` — Therefore, Bob must use at least

## Expected mathematical semantics

State records sequence generation rules, omitted values, index translation, and discrete-domain minimality.

## Current HML capability

HML can declare values and expressions but has no sequence state object, exclusion set, or index-translation semantics.

## Exact failure point

The sequence example needs omitted-value sets, index translation, successor iteration, and discrete minimality as persistent state; current HML has no sequence/exclusion state.

## Core/library/surface boundary

Core state representation candidate: unlike a theorem, the missing information must survive across transitions and affect later indexing.

## Smallest possible remedy

First-class neutral sequence metadata (generator/predicate, index convention, exclusions) plus generic finite-index evidence; defer syntax.

## Semantic impact

Proof state and denotation of indexed claims; rendering is secondary.

## Dependencies on other gaps

Depends on finite-domain enumeration, exact arithmetic, and candidate/minimality verification.

## Risk of overfitting Gold-25

Very high from one omitted-squares example; validate on recurrence, filtered sequences, and order-statistics examples before core changes.

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

First test whether a neutral sequence/exclusion state recurs; only then consider a reusable representation extension.
