# FINAL VERDICT: NO_MATERIAL_CLOSED_LOOP_HML_SIGNAL

GPU PORTABILITY: PASS

Mac/MLX vs A100/PEFT Top-1 agreement: 150/150 = 100.00%
Maximum score/logit deviation: 0.24855304
Maximum FP32 LoRA-update difference: 0

THEOREMS: 60

BASE SOLVED: 0/60 = 0.00%
RAW SOLVED: 0/60 = 0.00%
HML SOLVED: 0/60 = 0.00%

HML - RAW: +0.00pp
HML - BASE: +0.00pp
RAW - BASE: +0.00pp

## True horizon curve

| accepted-action horizon | BASE | RAW | HML | HML-RAW |
|---:|---:|---:|---:|---:|
| <=5 | 0/60 | 0/60 | 0/60 | +0.00pp |
| <=10 | 0/60 | 0/60 | 0/60 | +0.00pp |
| <=20 | 0/60 | 0/60 | 0/60 | +0.00pp |
| <=40 | 0/60 | 0/60 | 0/60 | +0.00pp |

## Source proof depth

| source depth | BASE | RAW | HML |
|---|---:|---:|---:|
| 6-10 | 0/20 | 0/20 | 0/20 |
| 11-20 | 0/20 | 0/20 | 0/20 |
| 21+ | 0/20 | 0/20 | 0/20 |

## Reliability and efficiency

| metric | BASE | RAW | HML |
|---|---:|---:|---:|
| rejection rate | 40.00% | 30.12% | 71.90% |
| recovery after rejection | 47.62% | 19.35% | 3.39% |
| total tokens / solved theorem | N/A | N/A | N/A |
| accepted actions / solved theorem | N/A | N/A | N/A |
| generated actions / solved theorem | N/A | N/A | N/A |

TOTAL PILOT WALL TIME: 3060.70s (51m 00.70s)

GPU UTILIZATION / BOTTLENECK SUMMARY: 640 five-second samples; mean SM utilization 29.90%, peak 100%; mean framebuffer use 26,013 MiB, peak 30,618 MiB. The bottleneck was sequential Lean episode initialization/execution plus single-stream autoregressive decoding, not GPU memory.

EXECUTION CAVEAT: Two frozen parents in every arm were rejected before model interaction because LeanDojo 2.0.0 cannot interact with declarations using `where`. The uniform executable-parent sensitivity is therefore also 0/58 for all arms. RAW additionally exceeded the pinned 40,960-token model context on six episodes; no truncation or arm-specific repair was applied.

DOES HML ADVANTAGE INCREASE WITH ACTUAL HORIZON: NO

DOES HML SOLVE MATERIALLY MORE COMPLETE THEOREMS: NO

NEXT SCIENTIFIC ACTION: STOP

FINAL_B: SEALED / UNOPENED
