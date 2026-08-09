# MATH-GAP-0004: Proof debt for non-reversible transformations

- Classification: `OBLIGATION_SYSTEM`
- Mathematical operation: `OBLIGATION_MANAGEMENT`

## Evidence in Gold-25

- `MATH-GOLD-002` `s4` — Taking the square root of 144, we see that $x + y = \boxed{12}$.
- `MATH-GOLD-004` `s1` — We can split the expression $|5x-1|=x+3$ into two separate cases.
- `MATH-GOLD-012` `s3` — There are two ways two dice add to 10: $4+6$ and $5+5$.
- `MATH-GOLD-012` `s8` — Adding the probabilities of these two cases gives us a total probability of $\frac{1}{72} + \frac{1}{72} = \boxed{\frac{1}{36}}$.
- `MATH-GOLD-019` `s6` — In either case, $x^{18} = \boxed{-1}$.
- `MATH-GOLD-025` `s6` — Therefore, Bob must use at least

## Expected mathematical semantics

Squaring, absolute-value branching, root extraction, and candidate elimination create obligations that persist until verified.

## Current HML capability

HML tracks rule/term obligations, but no generic source action can attach candidate-set or extraneous-solution debt to a transformation.

## Exact failure point

Non-reversible transformations and compressed case reasoning require debt to persist until a sign, coverage, or original-constraint check is discharged; current HML has no generic source-level debt attachment.

## Core/library/surface boundary

Obligation system: it extends proof-state accounting, not expression syntax or a domain theorem.

## Smallest possible remedy

Allow any operation to create typed obligations with provenance and explicit discharge evidence, including branch coverage and root-sign debt.

## Semantic impact

Proof state and epistemic status; it affects VERIFIED versus conditional/unsupported status, not mathematical denotation.

## Dependencies on other gaps

Depends on preconditions, candidate verification, case joins, and the existing mandatory-obligation engine.

## Risk of overfitting Gold-25

Low to moderate if obligations remain declarative and operation-agnostic; high if every textbook shortcut gets a bespoke obligation class.

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

Model transformation-created proof debt as first-class neutral obligations; do not silently mark textbook jumps verified.
