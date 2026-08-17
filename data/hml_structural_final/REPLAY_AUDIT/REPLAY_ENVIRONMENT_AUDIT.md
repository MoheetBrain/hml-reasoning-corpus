# Replay Environment Audit — Prover Instrumentation Pivot

Date: 2026-08-17. This is a new branch checkpoint after the passive-source verdict
`INSUFFICIENT_STRUCTURAL_DATA` at commit `18a3ba46cfdd8da84c34bd69443bfce4e37b0f98`.

## Recovered exact provenance

- Dataset: LeanDojo Benchmark 4, Zenodo DOI `10.5281/zenodo.12740403`.
- Archive SHA-256: `19b9a31968229d5bae4b959be9351d92740643d16a58c7f58f6d82795b8a98a4`.
- Mathlib repository: `https://github.com/leanprover-community/mathlib4`.
- Mathlib commit: `29dcec074de168ac2bf835a77ef68bbe069194c5`.
- LeanDojo version: `2.0.0`.
- Lean version recorded by the source provenance: `v4.10.0-rc1`.
- VM-installed Lean: `Lean 4.10.0-rc1`, commit `3b58e0649156`.
- VM-installed tools: `elan`, `lake`, and `lean`.

The recovered source provenance reconciles 241,265 canonical records plus 18,315
goal-creation exclusions to the historical 259,580 transition count. The canonical
records file SHA-256 is
`8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869`.

## Reconstruction status

**PARTIAL — exact toolchain identified; replay checkout not yet validated.** The VM
has approximately 1.5 GiB persistent disk free and 44 GiB RAM-backed `/tmp`. Any
Mathlib checkout/cache must remain in `/tmp`; no large installation was started in
this checkpoint. A detached VM audit log is retained at
`/home/moheet/HMLTN_CODEX_SYNTH/replay_environment_audit.log`.

No transition labels, synthetic records, HML semantics, or prior audit artifacts were
modified. The next operation is to reconstruct the exact Mathlib checkout in `/tmp`,
compile a minimal Lean witness, and then instrument only verified theorem families.

