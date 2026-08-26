# Solver Calibration

Status: `SOLVER_NOT_CALIBRATED`

The RAW-only development calibration solved 2 of 48 fresh theorem parents (4.1667%). This is below the frozen protocol's 10% minimum dynamic-range threshold. Per protocol, the run stopped after this reasonable calibration attempt; no HML arm was trained and no representation comparison was performed.

## Frozen development set

- Selection: deterministic hash order followed only by model-blind LeanDojo initialization compatibility
- Training-parent overlap: excluded
- Prior final/pilot-parent overlap: excluded
- Source actions exposed to solver: no
- Total: 48 theorem parents
- Source proof length 2–5: 24
- Source proof length 6–10: 16
- Source proof length 11–20: 8
- Compatibility replacements before freeze: 1
- `DEV_THEOREMS.json` SHA-256: `4c9c64a159f77ab79ea4530d65041357a4a8e6efad13951236ebd89791b6b1a6`

## Common solver attempt

- Representation used for calibration: RAW only
- Search width: 4
- Candidate generations per state: 4
- Maximum expanded states: 60
- Maximum proof depth: 40
- Solved: 2/48 (4.1667%)
- Wall time: 764.7039 seconds
- Development episodes SHA-256: `63577d5bb78b4ac39b6c0f3cc32985a1e670fd1972c58e1967f846ac68d99e4d`

## Protocol decision

The solver did not exceed the 10% floor. Evaluation theorems were therefore not frozen, the LOSSLESS_HML adapter was not trained, and FINAL_B remained sealed and unopened.
