# CPU preparation gate — required output before A100 start (mission §29)

```
CPU_PREPARATION_COMPLETE:      YES

HML_STANDARD_VERSION:          1.0
HML_STANDARD_COMMIT:           5e0fc61d9cf92eae9d3ce7c54299520cd3702f7c
HML_STANDARD_TAG:              hml-standard-v1.0-2026-08-27
HML_SEMANTIC_COMMIT:           b3d0af9ce5ed8d7c4d87086ceedd7e4fa5e74ad5
HML_REPRESENTATION_COMMIT:     b011511e72572608eb7836d3b8a1a6bb794c890d

50K_REGENERATED:               NO — superseded, see note below
OLD_50K_INVALIDATED:           YES — reports/INVALIDATED_INSTRUMENTATION_RUN.md
UTF8_PAYLOAD_AUDIT:            PASS — 0 literal escapes in all four arms of DATASET_V1
REPRESENTATION_PARITY:         PASS — 5,619 / 5,619, 16 properties, 0 failures
LABEL_LEAKAGE:                 PASS — all four arms

DATASET_V1_SIZE:               5,619 rows from 1,873 parent theorems
VALID_COUNT:                   1,873
INVALID_COUNT:                 1,873
UNRESOLVED_COUNT:              1,873

IID_SPLIT:                     READY — train 3,000 / dev 510 / test_iid 510
OOD_SPLITS:                    READY — alpha_rename 270, binder_depth 210,
                               dependency_depth 210, state_size 210,
                               composition 249, domain 450

PYTORCH_HARNESS:               READY
LINEAR_PROBE:                  READY
MLP_PROBE:                     READY
A100_SMOKE_TEST:               READY (CPU pipeline verified end to end; GPU smoke is
                               step 7 of run_gpu_experiment.sh)

ESTIMATED_STAGE1_GPU_TIME:     0.6 – 1.2 h wall
ESTIMATED_STAGE1_COST:         ~£3 – £6 at a2-ultragpu-1g on-demand

BLOCKERS:                      GPU capacity. europe-west4-a returns
                               ZONE_RESOURCE_POOL_EXHAUSTED (STOCKOUT) for
                               a2-ultragpu-1g + 1 local SSD.

USER_ACTION_REQUIRED:          Only if the stockout persists — see options below.
```

## Why 50K_REGENERATED is NO

Mission §3B asks for the 50K HML view to be regenerated once through the frozen renderer.
That was not done, and the reason is a measurement rather than a shortcut.

Regenerating it would have produced 50,000 clean rows of a corpus whose canonical state
carries **one claim and nothing else** — measured over 20,000 records: 1 claim, 0 candidates,
0 branches, 0 goals, 0 obligations, 1 scope, operation always `LEAN_TACTIC`. Eight of the
verifier's ten invariants have nothing to check on it, and the four arms would differ only in
how they wrap one opaque Lean string. Clean instrumentation would not have made it a
representation experiment.

What was done instead addresses the same defect at its source: the escape contamination was
introduced entirely at render time (the canonical source is clean — 0 literal escapes across
3,000 records), so building DATASET_V1 from that canonical source through the frozen renderer
produces uncontaminated text by construction. DATASET_V1 audits at 0 literal escapes in all
four arms.

The historical artifact is preserved and formally invalidated. Regenerating it remains
possible and is a small job if a use for 50,000 flat rows appears; it is not a prerequisite
for Stage 1.

## The number Stage 1 has to beat

A bag-of-words logistic regression with **no language model** reaches macro-F1 ≈ 0.68 on this
task, with a per-arm spread of 0.021. That, not the 0.333 class prior, is the bar. It is
wired into the harness as a per-arm control and into the headroom gate, and reported as
`probe_minus_own_bag_of_words_macro_f1`.

A probe that beats the prior but not its own arm's bag-of-words would have demonstrated that
the task has signal, not that the model reads mathematical state.

## Capacity options, if the stockout persists

| option | what it costs | what it risks |
|---|---|---|
| keep retrying `a2-ultragpu-1g` in europe-west4-a | nothing; the driver retries every 3 min | stockouts can last hours |
| switch the instance to `a2-highgpu-1g` (A100 **40GB**) in the same zone | a machine-type change on the existing VM | none technically — Qwen3-8B in bf16 is ~16 GB of weights, so 40 GB is ample at 8,192 context |
| rebuild in another zone | snapshot the boot disk, create a disk and VM elsewhere | more invasive; a new instance, and the local SSD does not travel |

The first is running. The second and third change the user's infrastructure and are not taken
without asking.
