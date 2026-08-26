# Lossless HML overlay — last defensible representation experiment

Frozen before representation-conditioned final evaluation.

## Hypothesis

The prior V1 semantic arm failed because it discarded exact mathematical content. This
experiment tests one replacement only: a lossless overlay that preserves the exact
available Lean state and completed tactic history while adding deterministic syntactic
indexes. It is compared with the strongest exact-history RAW control.

## Model and training

- `Qwen/Qwen3-8B`, revision
  `b968826d9c46dd6066d109eabc6255188de91218`, BF16, no quantization.
- Separate RAW and LOSSLESS_HML LoRA adapters: layers 28--35, `q_proj + o_proj`, rank 4,
  alpha 8 (scale 2), dropout 0, Adam, learning rate `1e-4`.
- Exactly 10,000 matched Lean transitions, identical parent/row order, one epoch,
  microbatch 1 and two-step gradient accumulation. Both targets are the exact next raw
  Lean tactic. Prompts and targets are masked so loss is computed only on the assistant
  tactic. No candidate ranking is used.
- Rows are deterministically selected from the existing HML50K train authority after
  requiring complete, untruncated RAW and LOSSLESS_HML chats to fit 3,072 tokens. This is
  a common selection gate, not an arm-specific truncation.

## Solver calibration

Calibration is RAW-only on 48 fresh development parents: 24 source proofs of length 2--5,
16 of length 6--10, and 8 of length 11--20. Parents from training, prior development/final
sets, FINAL_A, the previous closed-loop pilot, HML50K, and vNext are excluded. Selection is
hash-deterministic and model-blind. LeanDojo initialization compatibility is checked before
freezing the set; replacements use only the pre-frozen hash order.

The initial generic solver uses four beam-decoded tactic candidates per expanded state,
search width 4, at most 60 expanded states, and proof depth 40. Lean alone determines
successors. If RAW solves 20--50%, this solver is frozen. If RAW is 10--20%, one generic
budget increase to 100 expansions is allowed. If RAW remains below 20% after that, or is
below 10% on the initial attempt, calibration fails and representation research stops.
If the initial rate exceeds 50%, expansions are reduced once to 25. HML never participates
in calibration.

## Final evaluation

Only after calibration succeeds, freeze 100 new parents (minimum 60 if an external runtime
limit intervenes), stratified 40/35/25 over source proof lengths 2--5, 6--10, and 11--20.
The set is disjoint from both training views, calibration, FINAL_A, prior closed-loop pilot,
old final evaluations, HML50K, and vNext. Selection and LeanDojo compatibility filtering are
model-blind. FINAL_B remains sealed.

RAW and LOSSLESS_HML use the same model revision, solver, search and decoding budgets,
Lean/Mathlib environment, tactic action language, theorem order, and verifier. Success is
`ProofFinished`: zero goals and kernel acceptance. The primary endpoint is paired complete
theorem solve rate. A 10,000-draw paired theorem bootstrap with seed `20260826` provides the
95% interval for LOSSLESS_HML minus RAW.

## Decision rule

- Delta at most zero: `HANDCRAFTED_HML_REPRESENTATION_RESEARCH_TERMINATED`.
- Delta below +5pp, without at least 20% efficiency improvement or a clear increasing
  horizon advantage: the same termination verdict.
- Delta at least +10pp with paired evidence favoring HML:
  `LOSSLESS_HML_SIGNAL_FOUND`.
- Delta +5pp to +10pp, or a strong reproducible efficiency/horizon effect:
  `LOSSLESS_HML_POSITIVE_NEEDS_CONFIRMATION`.

No ontology redesign, representation tournament, larger training rung, FINAL_B access, or
automatic follow-on experiment is authorized.
