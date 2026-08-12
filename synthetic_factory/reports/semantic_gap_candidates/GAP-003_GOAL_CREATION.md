# GAP-003 — Goal creation is not representable

## Observation

18,315 of 259,580 original Lean transitions create goals and were excluded by the
canonical builder. Frozen HML deliberately fails closed when a transition creates a
new goal because goal ancestry, binder structure, scheduling and supersession are
not represented.

## Classification

`CORE_SEMANTIC_MISSING`, already documented by HML rather than newly discovered by
this factory.

## Smallest remedy

Before implementation, define goal identity and ancestry, parent/child relation,
binder/context inheritance, scheduling semantics and frame behavior. Add adversarial
tests for invented goals, lost parents, context leakage and false discharge. This is
a core semantic change and must be owned by the HML track, not this repository.

Stage100 does not depend on it. Future full-Lean coverage does.

## Exact blocked source and mutation

- Source population: 18,315 excluded Lean transitions marked
  `GOAL_CREATION_NOT_REPRESENTABLE` in `lean_exclusions.json`.
- Required meaning: a tactic introduces one or more legitimate child goals whose
  context, ancestry and future discharge remain linked to the parent transition.
- Current behavior: goal additions are rejected rather than guessed.

## Relevant files inspected

- frozen HML `src/hamiltonian_lang/semantic_state/model.py`
- frozen HML `src/hamiltonian_lang/semantic_state/verify.py`
- frozen HML `docs/hml_v2/SEMANTIC_STATE_CONTRACT.md`
- frozen HML `docs/hml_v2/OBLIGATIONS.md`
