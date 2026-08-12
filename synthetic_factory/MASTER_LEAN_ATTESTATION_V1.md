# Lean Runtime Evidence Attestation V1

## Executive verdict

Runtime replay works for the subset whose exact Lean state can be reconstructed from the
pinned trace, but **Stage100 fails** and Stage1k was correctly not run. Of 100 balanced
records, 32 are `REPLAY_PASS`; all 32 match both recorded states exactly. The dominant
blocker is that LeanDojo Benchmark 4 flattens enclosing and nested tactics into one list,
while its public runtime starts only at theorem entry. Fifty-six selected nested states
have no independently executable exact-state path in that representation.

| Decision | Result |
|---|---:|
| Exact replay environment reconstructed | YES |
| Stage100 | **FAIL** |
| Stage1k | NOT RUN — hard gate blocked it |
| Ready for broad Factory-B counterfactual generation | NO |
| GO / NO-GO | **LEAN_ATTESTATION_FIX_FIRST** |

This is not an HML defect and does not change HML. It is a Lean trace-to-runtime state
reconstruction limitation.

## Authority

| Authority | Exact identity |
|---|---|
| HML tag | `hml-semantic-pre-gemma-v1` |
| HML SHA | `84bf9897689b0ed78a2caaefc1db850d49b81260` |
| corpus SHA | `9d67e54450b9db897ee2ed20ec2e4cbbc16a3780` |
| Lean | `v4.10.0-rc1`; build commit `3b58e0649156` |
| mathlib4 | `29dcec074de168ac2bf835a77ef68bbe069194c5` |
| LeanDojo | package `2.0.0`; tag commit `abcfb72143ff3829e622418557e14c8b41b69a61` |
| source archive | DOI `10.5281/zenodo.12740403`; SHA-256 `19b9a31968229d5bae4b959be9351d92740643d16a58c7f58f6d82795b8a98a4` |
| canonical records | 241,265; SHA-256 `8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869` |
| theorem split | SHA-256 `2fddc0685f07ff85afb82da9fc40c7683fa0920ad8888937da9fb174f6a76637` |
| runtime environment digest | `86f30b7ee37a1a9b08c4099b6d7fbca8ef824388a74df9e4a92fa1a49e3618fc` |
| attestation code SHA | `f1e69af7639f7fecf98b903c4c85122adcadaf6331a531d575c8ac2dd9b30acd` |

The Zenodo archive was freshly downloaded and matched its 68,141,936-byte size, published
MD5, and full recovered SHA-256. The official LeanDojo `v2.0.0` tag resolved
unambiguously to the SHA above. The exact 2.58 GB traced mathlib cache was used; no Lean,
mathlib, or LeanDojo substitution occurred. HML remained clean and read-only.

## Architecture

```text
pinned canonical record + inherited theorem split
    -> recover exact theorem trace from Benchmark 4 random split
    -> construct an exact-text state graph (not flattened list order)
    -> start LeanDojo at the theorem declaration
    -> replay every exact graph edge to recorded state_before
    -> execute the exact recorded tactic in Lean 4.10.0-rc1
    -> collect Lean runtime result/state
    -> compare raw text, then transport-normalized text
    -> emit a provenance-bound, representation-neutral certificate
```

The graph step is necessary because benchmark `traced_tactics` contains enclosing compound
tactics and their nested child tactics. Treating list order as an executable proof prefix
was tested and rejected. Graph edges are joined only by exact state text; no state-equivalence
guess is used. Import-time GitHub metadata requests are blocked: executable content comes
only from the verified local traced checkout.

## Certificate contract

A `REPLAY_PASS` certificate guarantees all of the following:

- the pinned theorem/file/transition and inherited split IDs were used;
- Lean started in the pinned traced mathlib checkout under the pinned Lean toolchain;
- an exact recorded-state path was freshly replayed from theorem entry;
- runtime `state_before` matched the recorded state exactly or by the declared transport-only
  normalization;
- the exact recorded tactic was submitted to Lean;
- Lean accepted it, and runtime `state_after` matched the recorded state under the same rule;
- source, environment, action, raw/normalized state, backend result, and attestation-code
  digests are bound into the certificate.

It does **not** guarantee that a tactic is mathematically pedagogical, minimal, unique, or
appropriate for HML. It does not invent HML dependencies, evidence envelopes, obligations,
scope, or typed action arguments. For an intermediate open-goal transition, Lean has
elaborated the tactic and produced a valid proof state, but the whole theorem is not yet
closed; when the tactic closes the proof, LeanDojo additionally performs its kernel proof
type check. Trace presence alone remains `TRACE_ONLY`, never attestation.

Statuses are preserved distinctly: `TRACE_ONLY`, `REPLAY_PASS`,
`REPLAY_STATE_MISMATCH`, `REPLAY_TACTIC_FAIL`, `ENVIRONMENT_UNAVAILABLE`, and
`UNSUPPORTED`.

## Stage100

Selection scanned all 241,265 records and chose 100 unique theorems in 100 unique files
across 30 file families. It inherited the existing split and deliberately balanced the QA
sample rather than resplitting it.

| Dimension | Stage100 distribution |
|---|---|
| theorem split | TRAIN 80; DEV 10; FINAL 10 |
| effects | CLOSE 14; TRANSFORM_TARGET 14; each other effect 12 |
| proof depth | 0: 24; 1–2: 24; 3–7: 26; 8+: 26 |
| raw state length | S 23; M 26; L 24; XL 27 |
| hypothesis count | 0–8: 24; 9–13: 26; 14–19: 24; 20+: 26 |

| Replay status | Count | Rate | Exact cause |
|---|---:|---:|---|
| `REPLAY_PASS` | 32 | 32% | exact before, accepted tactic, exact after |
| `REPLAY_STATE_MISMATCH` | 11 | 11% | 9 target-entry and 2 prefix boundary mismatches |
| `REPLAY_TACTIC_FAIL` | 1 | 1% | one exact prefix edge returned `LeanError` |
| `ENVIRONMENT_UNAVAILABLE` | 0 | 0% | — |
| `UNSUPPORTED` | 56 | 56% | nested state has no exact executable path from theorem entry |

Runtime execution was reached for 44%; correct before-state reconstruction was 32%; and
the resulting-state match rate among executed target tactics was **100%**. The required
95%/95%/95% gate therefore fails on the first two measures. No source, split, or environment
substitution occurred.

## Hard audit

The second complete Stage100 run independently repeated all 100 records. The hard audit
selected the 15 highest-difficulty non-passes and five highest-difficulty passes. Every one
reproduced the same status and timestamp-excluded certificate content.

| # | Split | Effect | Depth | Result | Source transition |
|---:|---|---|---:|---|---|
| 1 | FINAL | CLOSE | 95 | UNSUPPORTED | `ContMDiffOn.contMDiffOn_tangentMapWithin::95` |
| 2 | FINAL | NO_VISIBLE_CHANGE | 95 | UNSUPPORTED | `MeasureTheory.snorm_le_snorm_fderiv_of_eq_inner::95` |
| 3 | TRAIN | CLOSE | 79 | UNSUPPORTED | `MeasureTheory.hasFDerivAt_convolution_right_with_param::79` |
| 4 | DEV | CLOSE | 69 | UNSUPPORTED | `ProbabilityTheory.kernel.iIndepFun.indepFun_finset::69` |
| 5 | TRAIN | REWRITE_CONTEXT_AND_TARGET | 56 | UNSUPPORTED | `Turing.ToPartrec.Code.exists_code::56` |
| 6 | TRAIN | CLOSE | 55 | UNSUPPORTED | `AkraBazziRecurrence.T_isBigO_smoothingFn_mul_asympBound::55` |
| 7 | TRAIN | TRANSFORM_TARGET | 52 | UNSUPPORTED | `SetTheory.PGame.quot_left_distrib::52` |
| 8 | TRAIN | NO_VISIBLE_CHANGE | 51 | UNSUPPORTED | `AlgebraicGeometry.exists_eq_pow_mul_of_isCompact_of_isQuasiSeparated::51` |
| 9 | TRAIN | REWRITE_CONTEXT | 51 | UNSUPPORTED | `Monotone.ae_hasDerivAt::51` |
| 10 | DEV | NO_VISIBLE_CHANGE | 47 | UNSUPPORTED | `Ring.DirectLimit.of.zero_exact_aux::47` |
| 11 | FINAL | INTRODUCE | 47 | UNSUPPORTED | `CategoryTheory.Pretriangulated.productTriangle_distinguished::47` |
| 12 | TRAIN | INTRODUCE_AND_TRANSFORM | 40 | UNSUPPORTED | `ProbabilityTheory.kernel.lintegral_compProd'::40` |
| 13 | TRAIN | REWRITE_CONTEXT | 38 | UNSUPPORTED | `FractionalIdeal.isPrincipal.of_finite_maximals_of_inv::38` |
| 14 | TRAIN | TRANSFORM_TARGET | 38 | UNSUPPORTED | `FiniteField.two_pow_card::38` |
| 15 | TRAIN | CLOSE | 36 | UNSUPPORTED | `CategoryTheory.isVanKampenColimit_extendCofan::36` |
| 16 | FINAL | CLOSE | 7 | REPLAY_PASS | `Set.PartiallyWellOrderedOn.fiberProdLex::7` |
| 17 | DEV | CLOSE | 7 | REPLAY_PASS | `HurwitzZeta.hasSum_nat_cosKernel₀::7` |
| 18 | TRAIN | INTRODUCE | 6 | REPLAY_PASS | `rat_mul_continuous_lemma::6` |
| 19 | TRAIN | INTRODUCE_AND_TRANSFORM | 2 | REPLAY_PASS | `SzemerediRegularity.distinctPairs_increment::2` |
| 20 | TRAIN | REWRITE_CONTEXT_AND_TARGET | 2 | REPLAY_PASS | `IsPurelyInseparable.tower_top::2` |

The difficult failures are not tactic rejection masquerading as a state mismatch. Their
recorded states occur inside compound tactic syntax, and no chain of recorded exact-state
edges connects theorem entry to those states. The detailed machine audit records full file,
theorem, split, effect, state size, status, backend phase, and independent content check.

## State matching

Comparison has four declared outcomes:

1. `EXACT_TEXT_MATCH` — byte-for-byte Unicode string equality;
2. `NORMALIZED_STATE_MATCH` — only CRLF/CR transport normalization, Unicode NFC, and
   terminal newline removal;
3. `SEMANTICALLY_EQUIVALENT_IF_PROVABLE` — reserved, but never inferred by V1 because no
   project mechanism currently proves proof-state equivalence;
4. `MISMATCH` — everything else, including binder renaming or proposition rearrangement.

Stage100 produced 32 exact before matches and 32 exact after matches. It produced zero
normalized-only or guessed-semantic matches. Raw and normalized hashes are both certified.

## Stage1k

**Not run.** The 44% runtime-execution and 32% correct-before-state rates are below the
required 95% thresholds. Scaling would only repeat a known reconstruction defect and would
violate the mission's hard gate.

## Runtime information available

| Information | Availability | Qualification |
|---|---|---|
| local hypotheses and types | YES | pretty-printed Lean state; not invented HML fields |
| focused goal and generated subgoals | YES | runtime pretty-printed goals, including goal count/order |
| binder structure | PARTIAL | Lean source/traced AST has structure; certificate currently hashes state text |
| exact tactic and textual arguments | YES | raw syntax submitted unchanged |
| typed tactic arguments | NO | not exported by this bridge |
| premise references | PARTIAL | source annotation may contain references; canonical rows do not uniformly expose them |
| tactic messages/errors | YES | preserved as typed backend result and digest |
| kernel result | YES WHEN CLOSED | LeanDojo validates the completed proof; open-goal steps expose accepted elaboration/state |
| HML dependencies/evidence/obligations/scope | NO | intentionally not synthesized |

## Performance

The benchmark used the 16 highest-difficulty Stage100 transitions already confirmed to
pass. Each timing includes theorem startup and exact prefix replay against a warm verified
trace cache. All worker counts reproduced the same certificate-set hash
`1b5758f03b44de3d3276a4d34b603c04619b9f0358fbdcc107365b48b4e4e0cc`.

| Workers | records/s | Wall time (16) | Peak process-tree RSS | Mean host CPU | Failures |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.314 | 50.89 s | 2.49 GB | 4.37% | 0 |
| 2 | 0.603 | 26.53 s | 3.90 GB | 8.40% | 0 |
| 4 | 1.154 | 13.87 s | 7.29 GB | 16.31% | 0 |
| 8 | 1.511 | 10.59 s | 13.16 GB | 22.13% | 0 |
| 12 | **1.728** | **9.26 s** | 19.42 GB | 26.52% | 0 |
| 16 | 1.669 | 9.59 s | 20.31 GB | 28.05% | 0 |

Twelve workers is the measured optimum for this sample. Sixteen adds memory and slightly
reduces throughput. The all-Stage100 12-worker run took 27.02 seconds, but that number
includes 56 immediate `UNSUPPORTED` outcomes and must not be presented as pure replay
throughput.

## Determinism

Stage100 was replayed twice from the same source SHA, environment digest, code SHA, and
configuration. Raw JSONL hashes differ because creation timestamps are required certificate
fields. After removing only the timestamp from the content commitment, both sets hash to:

```text
6f75541537776305d390fcea2d7bce55366fef6090fb8f1867a982d30f6ce306
```

All 100 statuses and all 20 hard-audit records reproduced. The performance benchmark also
produced one identical content hash at every tested concurrency.

## Split audit

Certificates inherit the existing theorem split; no resplitting occurs. The pinned split
contains TRAIN 192,882, DEV 24,067, and FINAL 24,316 records, with zero theorem overlap.
Stage100 preserves identity at 80/10/10. DEV and FINAL were used only for replay QA, not
training. Certificate descendants do not yet exist.

## Limitations

- Benchmark 4's flattened tactic list does not encode an executable entry operation for
  many nested tactic states.
- Eleven selected records still differ at an exact theorem-entry or prefix boundary, and
  one exact recorded prefix tactic returns a runtime `LeanError`; these require AST/position
  forensics, not normalization heuristics.
- No semantic proof-state equivalence checker exists, so binder-renamed or definitionally
  equal states are deliberately mismatches.
- The trace cache is large and currently resides in tmpfs on the replay VM.
- The bridge certifies Lean-native formal transitions only. It does not provide broad
  mathematical hard negatives or rich HML mappings.

## Factory-B impact

The 32 passing records prove the intended mechanism: for a freshly reconstructed real Lean
state, the exact observed action can be executed and its actual successor certified. Those
states can later support controlled nearby-tactic experiments with honest `SUCCESS`,
`FAIL`, `NEW_STATE`, and typed error outcomes. However, V1 does **not** unlock broad
Factory-B generation: 68% of the balanced sample lacks a certified target state. No
counterfactual negatives were generated in this mission.

## GO / NO-GO

**LEAN_ATTESTATION_FIX_FIRST.** The environment and certificate contract are sound, and
post-state fidelity is perfect where execution reaches the target. The reconstruction
coverage is far below the hard gate, so Stage1k and broad counterfactual generation remain
blocked. This result does not justify changing HML.

## Next atomic task

Build one AST-position-aware nested-tactic state navigator against the same pinned traced
cache, then rerun the **same Stage100** without changing its IDs or selection.
