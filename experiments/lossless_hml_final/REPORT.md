# FINAL VERDICT: SOLVER_NOT_CALIBRATED

RAW development solve rate after calibration: 2/48 = 4.1667%.

The frozen protocol required the RAW-only common solver to exceed a 10% development solve rate before representation research could continue. It did not. The experiment stopped without training LOSSLESS_HML, freezing evaluation theorems, opening FINAL_B, or running a RAW-versus-LOSSLESS_HML comparison.

## Calibrated solver attempt

- Search width: 4
- Candidate generations/state: 4
- Max expansions: 60
- Max depth: 40
- Development wall time: 764.7039 seconds

## Training

- RAW 10K: complete; 3303.5757 seconds; 5,602,834 tokens; adapter SHA-256 `e4ac761a814049870e12d339737f3dd5d7f71dd1679fbb5114c836f2d02d6916`
- LOSSLESS_HML 10K: not run due to mandatory protocol stop

## Evaluation

- Evaluation theorems: not frozen
- Evaluation episodes: 0
- RAW solved: N/A
- LOSSLESS_HML solved: N/A
- Delta and paired confidence interval: N/A
- Horizon, rejection, recovery, search-economics, and input-token metrics: N/A

## Decision

- Does advantage grow with horizon: N/A
- Does LOSSLESS_HML materially beat RAW: not tested
- Next action: `TERMINATE_HML_REPRESENTATION_RESEARCH`
- FINAL_B: sealed / unopened
