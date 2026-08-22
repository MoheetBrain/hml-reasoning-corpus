# HML50K build specification

Schema `HML50K_TEACHING_1.0.0` was frozen before generation. One canonical transition is
built once and projected into `HML_WORKED_UTF8` and `STRUCTURED_NEUTRAL_WORKED`.

- Authority: HML `68178f07784d2a17a9aed9c4dedbea9c740c97a0`; translation contract
  `vnext-translation-contract-1.0.0`; Mathlib source
  `29dcec074de168ac2bf835a77ef68bbe069194c5`.
- Canonical source SHA-256:
  `8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869`.
- Canonical state wrapper: raw Lean before-state is claim `p0/GIVEN`; raw after-state is
  claim `c1/DERIVED`, dependent on `p0`; evidence status is `FORMAL_TRACE`.
- Epistemic status is deliberately not called freshly replay-verified. The recorded trace is
  exact, and the VNext wrapper validates, but this mission did not run Lean.
- The safe action envelope contains the exact source `tactic_text`; action-derived premise
  annotations are retained in audit metadata and never inserted into the model state.
- `ensure_ascii=False` is mandatory. HML_TREE and crossed targets are not emitted.
- Official LeanDojo train/val/test splits map to TRAIN/DEV/FINAL. All 3,670 old VNext parents
  are excluded. Near duplicates are removed with holdout priority FINAL > DEV > TRAIN.
- The Qwen3-8B tokenizer preflight removes 34 intact transitions that would exceed the
  6,144-token raw input+target gate in at least one paired task. Nothing is truncated.

Tasks are `NEXT_ACTION_SELECT` (primary), `STATE_DELTA_PREDICT`, `VALIDITY_JUDGE`, and
`WORKED_CONTINUATION`. Judge negatives are `UNRESOLVED`, not invented `INVALID` labels.
Each action-selection row has six deterministically ordered candidates: the recorded gold
action and five distinct plausible actions, mined by same head, effect family, then
length-nearest split-wide fallback.

TRAIN rungs are deterministic prefixes of one curriculum order: 10K ⊂ 30K ⊂ 50K.
The executable specification is `schema_selection_spec.json`; the builder is
`scripts/hml50k/build_hml_50k.py`.
