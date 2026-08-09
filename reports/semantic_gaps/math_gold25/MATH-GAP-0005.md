# MATH-GAP-0005: Domain theorem and formula library interface

- Classification: `LIBRARY_THEOREM`
- Mathematical operation: `APPLY_THEOREM`

## Evidence in Gold-25

- `MATH-GOLD-001` `s1` — For the piecewise function to be continuous, the cases must "meet" at $2$ and $-2$.
- `MATH-GOLD-001` `s2` — For example, $ax+3$ and $x-5$ must be equal when $x=2$.
- `MATH-GOLD-001` `s4` — Similarly, $x-5$ and $2x-b$ must be equal when $x=-2$.

## Expected mathematical semantics

Named theorems such as continuity boundary matching, AM-GM, Pythagorean theorem, tangent addition, parity, and digit-sum divisibility carry hypotheses and checked conclusions.

## Current HML capability

HML can represent propositions and checked closed/definition evidence, but the trusted core has no domain theorem registry or hypothesis-aware theorem evidence.

## Exact failure point

The continuity, theorem, or formula step can be written as a proposition, but no current trusted evidence object binds theorem hypotheses to its conclusion.

## Core/library/surface boundary

Library theorem: the generic APPLY_THEOREM operation belongs in the core; continuity/AM-GM/Pythagorean/etc. facts belong in audited libraries.

## Smallest possible remedy

A theorem-library manifest and replayable evidence format carrying theorem ID, hypotheses, conclusion, and checker.

## Semantic impact

Denotation is unchanged; operational verification and epistemic status become stronger when evidence is trusted.

## Dependencies on other gaps

Depends on precondition obligations, typed expressions, and dependency/provenance tracking.

## Risk of overfitting Gold-25

High if theorem names become core keywords; require generic theorem application with data-driven library entries.

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

Build a separately audited theorem-library/evidence protocol; keep theorem names out of the core instruction set.
