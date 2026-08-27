# EXP_REP_VALIDITY_V1 — max-EV representation experiment

**The question.** Does frozen HML make mathematical state easier for a pretrained model to
read and act on than matched alternative representations?

**The method.** One canonical semantic object per item, rendered four ways; the labels come
from the frozen HML verifier; sequential stages, each cheap enough that a negative result is
affordable and each gated so a miscalibrated instrument stops the run rather than producing a
confident number.

## Frozen inputs

| what | identity |
|---|---|
| HML semantics | `b3d0af9ce5ed8d7c4d87086ceedd7e4fa5e74ad5` / `hml-semantic-freeze-vnext-2026-08-27` |
| HML model language (renderer) | `b011511e72572608eb7836d3b8a1a6bb794c890d` / `hml-model-language-v1-freeze-2026-08-27` |
| HML Standard | `1.0` / `5e0fc61d9cf92eae9d3ce7c54299520cd3702f7c` / `hml-standard-v1.0-2026-08-27` |
| renderer | `semantic_state/view.py` (`R6_SHIPPED_VIEW`), used as frozen, not re-implemented |

## Layout

```
canon/      lean_state.py       decompose a recorded Lean tactic state into its components
            build_canonical.py  -> one canonical Transition per item
            alpha_rename.py     consistent binder renaming (OOD split A, memorisation control)
arms/       common.py           model-facing projection + the shared IR
            hml.py              R_HML   -- calls the frozen view
            typed_ast.py        R_TYPED_AST
            leanlike.py         R_LEANLIKE
            structured_english.py R_STRUCTURED_ENGLISH
mutate/     mutations.py        16 causal mutation families, labelled by the verifier
            distractors.py      uncited records, so the task is not keyword spotting
audit/      unicode_payload.py  decoded-payload escape audit (§3A)
            parity.py           representation parity gate (§5)
            leakage.py          six-channel leakage audit (§5)
dataset/    build_v1.py         DATASET_V1: 5,619 rows, balanced, split by theorem
harness/    extract.py          frozen-model pooled features
            probe.py            linear (Stage 1) and matched MLP (Stage 2)
            baselines.py        class prior + bag-of-words control
            metrics.py          macro-F1, calibration, information gain, paired statistics
            stage1.py           the orchestrator
```

## Why the canonical object is built rather than taken

The 50K corpus wraps each Lean step as a transition whose prior state holds exactly **one**
claim: the entire tactic state as one string. Measured over 20,000 records, every state has
1 claim, 0 candidates, 0 branches, 0 goals, 0 obligations, 1 scope and the operation
`LEAN_TACTIC`. Eight of the verifier's ten invariants have nothing to check there, and four
ways of wrapping one opaque string is not a representation comparison.

The structure was never missing from the data, only from the wrapper: a Lean tactic state
already *is* a typed context plus a goal. `canon/` recovers it — 99.9% of 20,000 records
decompose cleanly, averaging 12.5 typed declarations, 100% with an explicit goal and 42% with
a case label. Every identifier, type and proposition is copied verbatim.

## Why the labels are built by mutation rather than taken

Measured over `vnext_10k`, the verifier's natural verdict is almost perfectly predicted by
the operation name alone: LEAN_TACTIC 4000/4000 VALID, SOURCE_DERIVATION 2000/2000
UNRESOLVED, OPEN_BRANCH 61/61 INVALID. A dataset drawn from that distribution measures a
token lookup.

So each parent contributes a matched triple — itself as VALID, one causal mutation as
INVALID, one as UNRESOLVED — sharing operation, domain, source theorem and every structural
feature. Operation-name and Mathlib-area mutual information with the label are both **0.000
bits** as a result.

## Gates

| gate | where | status |
|---|---|---|
| Standard frozen | mission §1 | PASS — 1.0, clean, tagged, pushed |
| decoded-payload escapes = 0 | §3D | PASS — 0 in all four arms |
| representation parity | §5 | PASS — 5,619/5,619, 16 properties |
| leakage | §5 | PASS — all four arms |
| headroom | §13 | evaluated at run time, on controls and dev only |

## Running it

```bash
# CPU: rebuild the dataset and re-run both gates
PYTHONPATH=. python -m experiments.max_ev_representation_v1.dataset.build_v1
PYTHONPATH=. python -m pytest experiments/max_ev_representation_v1/tests -q

# CPU: full pipeline check with no model (validates probes, metrics, splits, statistics)
PYTHONPATH=. python -m experiments.max_ev_representation_v1.harness.stage1 \
    --synthetic-encoder --device cpu --seeds 0 1 2

# GPU: Stage 1 on the A100, start to stop
./experiments/max_ev_representation_v1/run_gpu_experiment.sh EXP_REP_VALIDITY_V1
```

## What Stage 1 must clear

Not the class prior. A bag-of-words logistic regression with no language model reaches
**macro-F1 ≈ 0.68** on this task (per-arm spread 0.021). A probe that beats the prior but not
its own arm's bag-of-words has shown the task has signal, not that the model reads
mathematical state. `probe_minus_own_bag_of_words_macro_f1` is reported per arm per split for
exactly that reason.
