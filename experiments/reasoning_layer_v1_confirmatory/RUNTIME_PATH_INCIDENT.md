# Runtime path incident

On 2026-08-24, the external artifact and ML runtime directories were relocated from
`/Users/moheet/` to `/Users/moheet/Projects/Hamiltonian-Labs/` while the first BASE seed-1
attempt was running. The active checkpoint destination disappeared at iteration 1,900, so
that attempt failed before completion and before any FINAL_A scoring. A compatibility
symlink was then replaced during a second startup attempt, which failed while loading the
training dataset and performed no training iterations.

Both failed-attempt logs and the first attempt's partial checkpoints are preserved under
the external experiment artifact directory in `incidents/`. They are excluded from all
analyses. The driver now names the relocated canonical paths directly. No model recipe,
dataset content, arm content, seed, evaluation rule, or statistical gate changed. Preflight
must be rerun after this path-only amendment, and training restarts from iteration zero.

After BASE seed 1 later completed successfully, a laptop shutdown interrupted the first
RAW seed-1 startup before any training-loss checkpoint (the log contains validation only).
That startup log and empty adapter shell are preserved in `incidents/laptop_shutdown_raw_seed1/`
and excluded from analysis. RAW seed 1 restarts from iteration zero with the same frozen
recipe and prepared dataset; the completed BASE adapter is retained unchanged.
