# HML closed-loop theorem-solving pilot

Frozen development protocol for the three-arm, no-training pilot on the existing
reasoning-layer V1 adapters.

## Scientific question

Does the frozen V1 semantic representation cause Qwen3-8B to solve materially more
complete, unseen Lean theorems than the frozen raw-history representation or current
state alone?

## Frozen assets

- Model: `Qwen/Qwen3-8B`, revision
  `b968826d9c46dd6066d109eabc6255188de91218`, native BF16, no quantization.
- Adapters: seed-1 BASE, RAW, and SEMANTIC adapters frozen by the V1 FINAL_A run.
- Adapter conversion: MLX matrices are transposed and renamed into PEFT; rank 4,
  alpha 8, dropout 0, ordinary LoRA scaling, layers 28--35, `q_proj + o_proj`.
- Lean: LeanDojo Benchmark 4 Mathlib commit
  `29dcec074de168ac2bf835a77ef68bbe069194c5` and its declared Lean toolchain.
- HML semantics and the V1 extractor are unchanged. FINAL_B remains sealed.

## Theorem envelope

Exactly 60 parent theorems are selected deterministically from the unused remainder of the
LeanDojo Benchmark 4 random training split: 20 with source proof length 6--10, 20 with length 11--20, and
20 with length 21+. Parents and normalized initial states occurring in HML50K, vNext,
reasoning-layer TRAIN/DEV/FINAL_A, or prior final evaluation are excluded. Thus the source
split label does not place any selected parent in the model's actual training envelope. Exact
normalized duplicate initial states are excluded. `theorems.json` is the frozen authority.
Source proof tactics are not copied into that file or exposed during evaluation.

## Arms and information contract

Every arm sees the actual current Lean state and equivalent verifier-error information.
BASE sees no successful history. RAW additionally sees the exact last four successful
`(state_before, action, state_after)` events and the total accepted-action count. HML sees
the unchanged V1 semantic extraction of the same current state and successful prefix.
Rejected tactics and their Lean errors are supplied identically, outside the arm-specific
representation payload. No arm sees source actions, gold tactics, candidates, future
states, or gold-derived metadata.

All arms emit the same object: one raw executable Lean tactic. The prompt has no system
message, uses the pinned tokenizer chat template with thinking disabled, and requests only
the tactic. Greedy decoding, `do_sample=false`, and `max_new_tokens=128` are identical.

## Closed-loop budget and success

Each theorem starts at S0. Lean-accepted tactics advance the persistent Dojo state;
rejected tactics leave it unchanged. Budgets are 40 accepted actions, three rejected
retries at one state, and 60 total generations. Success requires `ProofFinished`, which
is Lean kernel acceptance with zero remaining goals.

## Gate and execution

Before evaluation, conversion must pass exact FP32 update equivalence, inventory checks,
and a 50-row frozen FINAL_A parity sample. Material policy-parity failure stops the pilot.
The base model remains resident on one A100 80GB GPU; adapters are switched without model
reload. Independent persistent Lean episodes may run concurrently, while greedy model
calls are serialized on the resident GPU.

Primary endpoint is complete Lean-verified solve rate. Secondary outputs are solve rates
by accepted-action horizons 5/10/20/40, source-depth strata, rejection and recovery rates,
token/action efficiency, failures, and wall time. Verdict thresholds and stopping rules
are those in the user-authorized closed-loop specification. No larger experiment is
automatically authorized.
