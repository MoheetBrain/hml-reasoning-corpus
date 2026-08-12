# GAP-002 — Arbitrary Lean validity lacks a current evidence checker

## Observation

Frozen HML can preserve externally adjudicated replay evidence and can require
runtime `CheckedEvidence`, but the current certificate registry does not execute an
arbitrary Lean theorem/tactic state transition. Proposition bodies are intentionally
opaque strings to the semantic-state verifier.

## Classification

`LIBRARY_MISSING` / trust-integration gap, not evidence that HML denotation or core
state-transition semantics are wrong.

## Smallest remedy

Specify a Lean checker adapter that binds theorem environment hash, Lean/mathlib
version, before-state, tactic and after-state into an unforgeable runtime attestation.
Keep OFFLINE_REPLAY and RUNTIME labels distinct. This belongs in a checker/library
integration unless the integration reveals a missing generic evidence field.

No generated positive may copy `VERIFIED` status into runtime trust.

## Exact blocked source and mutation

- Source: any canonical Lean row proposed for a runtime-certified valid/invalid pair.
- Required meaning: the exact tactic transforms the exact elaborated Lean goal state
  under the pinned environment.
- Current behavior: `verify_replay` can consume imported status; `verify_runtime`
  fails closed without checker-produced attestations. This factory records those
  modes separately.

## Relevant files inspected

- frozen HML `src/hamiltonian_lang/semantic_state/trust.py`
- frozen HML `src/hamiltonian_lang/semantic_state/verify.py`
- frozen HML `docs/hml_v2/SEMANTIC_STATE_CONTRACT.md`
- frozen HML `docs/hml_v2/MATHEMATICAL_LIBRARY_CONTRACT.md`
