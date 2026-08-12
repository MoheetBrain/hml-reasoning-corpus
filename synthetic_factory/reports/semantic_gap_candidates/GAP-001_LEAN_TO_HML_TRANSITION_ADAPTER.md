# GAP-001 — Lean records are not verifier transitions

## Observation

The pinned 241,265-record Lean artifact records theorem state text, observed tactic,
resulting state text and goal deltas. It does not encode HML `SemanticState`, typed
`Action`, dependencies, preconditions, obligations, branches/scopes, candidates,
goals or evidence envelopes. Its `premises_used` list is empty in all records.

## Classification

`TRANSLATION/CANONICALIZATION_PROBLEM`, not a demonstrated HML-core defect.

## Smallest remedy

Build a read-only, provenance-preserving qualification adapter that maps only
semantics supported by the source trace, emits explicit `NOT_REPRESENTABLE` for
missing information, and requires every emitted transition to replay `VALID` under
the frozen verifier. Census frame-condition conflicts before generating negatives.

Do not infer dependencies or proof debt from tactic spelling. Do not modify HML.

## Exact blocked source and mutation

- Source: `lean_canonical_records.jsonl`, SHA-256
  `8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869`.
- Blocked operation: construct an HML `Transition` before proposing any one-field
  counterfactual mutation.
- Current behavior: the Lean row cannot be passed to `import_transition`; its state
  and action objects implement a different effect-first schema.

## Relevant files inspected

- corpus `experiments/lean_domino_v2/dataset/lean_canonical_records.LOCATOR.json`
- exported `build_lean_canonical.py`
- frozen HML `src/hamiltonian_lang/semantic_state/model.py`
- frozen HML `src/hamiltonian_lang/semantic_state/neutral.py`
- frozen HML `src/hamiltonian_lang/semantic_state/verify.py`
