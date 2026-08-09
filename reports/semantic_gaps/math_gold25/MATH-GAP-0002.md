# MATH-GAP-0002: Candidate generation and original-constraint verification

- Classification: `VERIFIER_GAP`
- Mathematical operation: `VERIFY_CANDIDATE`

## Evidence in Gold-25

- `MATH-GOLD-004` `s1` — We can split the expression $|5x-1|=x+3$ into two separate cases.
- `MATH-GOLD-004` `s3` — If we plug this value of $x$ back into the original equation in order to check our answer, we see that $|5(1)-1|=1+3$ or $4=4$.
- `MATH-GOLD-004` `s5` — If we plug $-\frac13$ back into the initial equation, we get that
- `MATH-GOLD-004` `s6` — the final answer is the larger of the two
- `MATH-GOLD-015` `s6` — $\boxed{34}$ is the smallest solution since it is a lower bound of $a$ and satisfies both original congruences.
- `MATH-GOLD-025` `s6` — Therefore, Bob must use at least

## Expected mathematical semantics

A candidate produced by solving or branching is checked against the original equations/inequalities and domain before acceptance.

## Current HML capability

closed_eval_v1 checks closed exact propositions; current HML has no generic candidate object or verifier linking candidate provenance to original constraints.

## Exact failure point

A solver/case step produces a candidate, but current HML has no first-class link from that candidate to the original constraint, domain, and acceptance decision.

## Core/library/surface boundary

Verifier interface: candidate objects and checks can be expressed as claims/evidence without changing the core expression denotation.

## Smallest possible remedy

A neutral candidate record plus a verifier obligation that cites the original constraint and reports valid/invalid/undetermined.

## Semantic impact

Proof state and epistemic status; accepted candidate denotation is unchanged.

## Dependencies on other gaps

Depends on provenance, exact/closed evaluation, domain preconditions, and case/solver outputs.

## Risk of overfitting Gold-25

Moderate; avoid a protocol tied only to polynomial roots or inequality thresholds.

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

Expose candidate verification as a neutral evidence/obligation interface, likely library-backed, without making solver output trusted by assertion.
