# HML Research State

Checkpoint date: 2026-08-26 (Europe/London)

This is the authoritative new-thread handoff for the current research queue. Chat history is
not project memory. No heavy job is active.

Recovery order: `AGENTS.md`, this file, `docs/PROJECT_STATUS.md`,
`docs/PROJECT_LEDGER.md`, `STATUS.json`, Git HEAD/status, then only the relevant frozen
report and protocol.

## Current project and question

**Current project:** Hamiltonian Lang / HML.

**Current scientific question:** Is the observed HML representation advantage real, and if
so what layer causes the remaining failures and what experiment should come next?

## Important current result

The frozen `FINAL_HML_SIGNAL` depth-conditioned one-step action-selection experiment reported:

- HML10K two-seed mean: **85.75%**
- Neutral10K two-seed mean: **50.20%**
- HML minus Neutral: **+35.55 percentage points**
- Parent-clustered paired 95% CI: **[+33.53, +37.50]pp**
- Seed 1 delta: **+35.20pp**
- Seed 2 delta: **+35.90pp**

Result authority:

- Frozen experiment: `FINAL_HML_SIGNAL`
- Result commit: `701f99ec137326a91e8d61faae686a3baf5f0120`
- Result repository/checkout: `/Users/moheet/Documents/ChatGPT/hamiltonian-lang-final-signal`
- Result repository remote: `https://github.com/MoheetBrain/hamiltonian-lang.git`
- Report: `experiments/final_hml_signal/FINAL_SIGNAL_REPORT.md`
- Report SHA-256: `52175ab852d3385251408b26fc91c580a26c460619c02c64548ac7571615413f`
- Protocol: `experiments/final_hml_signal/FINAL_SIGNAL_PROTOCOL.md`
- Protocol SHA-256: `163872e1d26311a099f9167e01f20a49f6d91b1360c9e5321d6cf88fab3dfa5e`

The exact frozen report and protocol are copied into this repository. The result commit
belongs to the Hamiltonian Lang repository, not this corpus repository; do not mistake a
failed `git show 701f99e` here for a missing experiment.

## Scientific status and caveat

The +35.55pp headline is a major positive signal that requires forensic false-positive
analysis before it can be treated as a genuine mathematical-reasoning representation
result. It is **depth-conditioned one-step action selection**, not free-running long-horizon
theorem solving. Long-horizon reasoning is not proven.

The current corpus authority is `HML50K_READY`: 50,000 TRAIN, 3,000 DEV and 3,000 FINAL
matched records. Immutable payload commit: `fb6e28edec0f77753d97486cbae759a59f1d1f38`;
reporting commit: `627194144abd9396dadbebf0b7834e76b937d908`.

## Mandatory next scientific priority

Perform a forensic audit of the +35.55pp result. It must check, at minimum:

1. independent scorer reproduction;
2. adapter/checkpoint correctness;
3. exact HML/Neutral FINAL pairing;
4. train/FINAL duplication and near-duplication;
5. gold/future-derived input leakage;
6. candidate surface leakage;
7. target/output asymmetry;
8. the lexical-failure subset;
9. untouched base-model HML versus Neutral;
10. scoring-normalization robustness;
11. 50 HML-win/Neutral-loss manual cases;
12. 50 reverse/failure cases; and
13. cross-view adapter diagnostics.

Do **not** run 30K until the headline survives this complete checklist.

## Required reconciliation before new execution

The filesystem contains later evidence and it must not be erased or silently ignored:

- Hamiltonian Lang commit `9a1cd5dd6f219ab6d52b2edc2b511c85afdd3bf2` records an initial forensic audit, but its
  report explicitly skipped untouched-base and cross-view inference. It therefore does not
  satisfy the stricter minimum checklist above by itself.
- Hamiltonian Lang commit `4bbd71c86c6650265679c565e12a48630ef4b58f` records a later common-envelope control:
  HML 85.33%, Neutral 88.10%, delta **-2.77pp**, 95% CI **[-3.72, -1.81]pp**. Its report says
  the original +35.55pp was an arm-specific envelope confound. Frozen handoff commit/tag:
  `273a5145fb4128daf37493de396126aa8cc84d97` /
  `common-envelope-10k-final-20260824`.
- This corpus branch subsequently recorded a free-running solver calibration stop at parent
  commit `d6f03ea8b99236f5e1b727c36c74e2717a8faeba`: RAW solved 2/48 (4.17%), below the frozen
  10% floor, so LOSSLESS_HML training/evaluation did not run.

Consequently, the next thread must treat **forensic reconciliation of all frozen evidence**
as the next action, not blindly rerun the old audit or start another experiment. The
+35.55pp number remains an important observed result, but the latest causal evidence does
not support interpreting it as an HML state-serialization advantage.

## Preferred causal and long-term sequence

If the complete forensic review leaves a live signal, the preferred causal test is a
COMMON-TARGET 10K control in which HML and Neutral inputs predict the exact same
representation-independent candidate label A-F. The existing common-envelope C0-C5 control
appears to instantiate this idea and must be audited before any rerun is proposed.

Only after a common-target effect survives should the project build an actual Lean
free-running theorem-solving evaluation. Only after that should HML representation evolution
or recursive optimization begin.

Project rule: no HML-V2, no random language redesign, and no semantic, policy or search
change before diagnosing the failure layer.

## Large local artifacts deliberately outside this Git repository

The final-signal external artifact root is
`/Users/moheet/Projects/Hamiltonian-Labs/hml_research_artifacts/final_hml_signal/`
(approximately 434 MB). The four final adapter hashes are:

- HML seed 1: `b77ad4fb31b190581b9c6c1f675840f310e471a179b9c82854a7f12523a2fbc3`
- Neutral seed 1: `eb0b119c365a320f43257d84df39beec99ff48fe3874e3d8b1d30762261ef047`
- HML seed 2: `61155b810f110c2eaae78bf3ac4562e86eb434ceb6c24dfde63a1a4b13a4cb4e`
- Neutral seed 2: `8f54204a08402f3c1d337d981c7065378ad26bda5f70230d01a4143e774b7e50`

Do not add model weights, intermediate checkpoints, caches or the external artifact root to
this repository.
