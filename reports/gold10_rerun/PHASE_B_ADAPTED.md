# Gold-10 Phase-B adapted rerun and final handoff

This is the controlled rerun of the identical ten trajectories and 23 canonical
transitions. Phase A froze the pure-repin result before any renderer changes. Phase B
then changed only corpus renderings and pin/support metadata; it did not modify
`hml_core`, canonical states, canonical actions, transition order, mathematical
answers, warrants, dependencies, domains/types, or oracle judgments.

## Final report — exactly 26 requested items

### 1. Corpus BASE SHA

`467a4866756e6653c1b618a1eed479cda8d5927a` on branch `main`.

### 2. Corpus FINAL SHA

The single handoff commit created after this report is staged; its exact SHA is
reported in the delivery message because a commit cannot contain its own hash.

### 3. OLD HML SHA

`164d1946e91216c093478132caa0d06427259682`.

### 4. NEW HML SHA

`5688aba18632b65a8709aa1d85577d31a67dba6a`, resolved unambiguously after fetching
the authoritative Hamiltonian Lang repository.

### 5. Confirmation that only the HML pin changed in Phase A

Confirmed. The pre-repin baseline was recorded first. Phase A changed the submodule
gitlink and project HML metadata only. The old corpus renderer was run before Phase-B
adapter changes.

### 6. Phase-A pure-repin results

The unchanged ten HML renderings all returned exit code 0 against the new HML. The
unchanged corpus test suite itself returned 1 for two expected old-pin assertions:
the pin guard still saw the old gitlink until the new gitlink was staged, and the old
test hard-coded the old SHA. Behaviorally, the unchanged renderings preserved all 11
native passes; G06 and G07 stayed open; G03, G09, and G10 still had no emitted
evidence/library inference. New HML probes passed for certified underdetermination,
quantifier core, exact evaluation, definition unfolding, unknown-vs-underdetermined,
and the static checker registry.

### 7. Phase-B adapter changes

The corpus renderer now emits `closed_eval_v1` for G01, G02, G09, and the numeric
G10 substep; `definition_unfold_v1` for all three G03 steps; and the exact
`propositional_underdetermination_v1` plus `undetermined` path for G06. Header pins,
rendering metadata, project metadata, and pin-aware tests were updated. No HML source
file was edited.

### 8. Phase-B results

All ten adapted HML programs return exit code 0. G06 reaches `UNDERDETERMINED`; all
previous native proof paths remain valid; eight formerly adapter-blocked transitions
now have valid checked-certificate paths. G07:a1, G09:a0, G10:a1, and the full
G10:a2 transition remain unsupported for library reasons only.

### 9. 23-transition before/after matrix

The complete matrix is in [GOLD10_BEFORE_AFTER.md](GOLD10_BEFORE_AFTER.md), with
machine-readable dimensions and behavior in [PHASE_B_ADAPTED.json](PHASE_B_ADAPTED.json).

### 10. Old CoreGapRate

`2/23 = 8.70%` after the prior forensic classification: G06:a1 and G07:a1.

### 11. New CoreGapRate

`0/23 = 0.00%`. G06 is closed by the new certified epistemic path. G07’s generic
quantifier core is present; its remaining body theorem is a library/evidence issue,
not a new universal core semantic.

### 12. NativeKernelVerificationRate

`11/23 = 47.83%`. These are the unchanged native kernel transitions.

### 13. CheckedCertificateVerificationRate

`8/23 = 34.78%`. These are G01:a2, G02:a1, G03:a0..a2, G06:a0..a1, and G09:a1.
G10:a2 has a checked numeric substep but is not counted here because the full
transition still requires a derivative theorem.

### 14. LibraryBlockedRate

`4/23 = 17.39%`: G07:a1, G09:a0, G10:a1, and G10:a2 as full transitions.

### 15. CorpusAdapterGapRate

Phase A: `8/23 = 34.78%`. Phase B: `0/23 = 0.00%`. The eight Phase-A adapter
gaps were resolved without changing canonical mathematics.

### 16. Regressions

No regressions. The 11 previously native-verified transitions remain valid, all ten
adapted programs compile, and no new failure was observed. The changed classifications
are G06:a0, G06:a1, G07:a1, G09:a0, G10:a1, and G10:a2; these are classification/path
changes, not changed mathematical judgments.

### 17. GAP-0003 final status

Closed as a corpus adapter over repaired HML core semantics. The core now checks a
context-relative pair of complete models and projects the result as
`UNDERDETERMINED`. The adapted G06 rendering obtains that result. `UNKNOWN` remains
distinct from `UNDERDETERMINED`.

### 18. GAP-0004 final status

No longer a core-semantic gap. `forall_intro` and `forall_elim` pass generic
round-trip, domain, eigenvariable, freshness, scope, and capture probes. The exact
Gold-10 body `n + 0 = n` remains unsupported without trusted symbolic/theorem evidence.

### 19. GAP-0001 and GAP-0002 final status

Both are corpus adapter/certificate-boundary issues, not missing arithmetic or
definition semantics. Existing HML-owned exact evaluation and definition unfolding
are admitted through registered checked evidence and now validate the same G01/G02/G03
steps.

### 20. Confirmation GAP-0005 and GAP-0006 remain library-level

Confirmed. Conditional-probability product inference remains a probability-library
capability. Reciprocal differentiation remains a calculus-library capability. Exact
numeric execution can be checked separately, but it cannot manufacture the missing
probability or derivative theorem.

### 21. Tests

Passed: all ten direct HML checks; canonical trajectory/oracle tests; pin-aware Gold-10
tests after the final gitlink is recorded; schema validation; read-only/clean checks;
the corpus-side rerun script `tests/test_gold10_rerun.py`; and all listed security
probes. The security probes rejected stale context, wrong context, forged evidence,
unregistered checkers, wrong-domain elimination, witness-specific introduction, and
binder capture, while keeping unknown goals open.

### 22. Exact corpus commit

The exact final corpus commit is the atomic handoff commit reported by `git rev-parse
HEAD` in the delivery response. Its parent is the corpus base in item 1; no second
commit is made for this mission.

### 23. Git submodule status

The final expected line is:

```text
5688aba18632b65a8709aa1d85577d31a67dba6a hml_core (hml-m2-context-budget-49-g5688aba)
```

### 24. Confirmation `hml_core == 5688aba`

Confirmed: `git -C hml_core rev-parse HEAD` resolves to
`5688aba18632b65a8709aa1d85577d31a67dba6a`.

### 25. Confirmation `hml_core` remains read-only and clean

Confirmed after every HML execution: `git status --porcelain` is empty and no file
under `hml_core` has any write bit (`find hml_core -type f -perm -022` is empty).

### 26. Recommendation

**REPAIR_AND_RERUN_GOLD10.** HML core design is not fundamentally wrong: the two
genuine core gaps are closed, the new certificate boundary is sound, and there are no
regressions. Do not proceed to Gold-100 yet. First add or select trusted library-level
evidence for the four blocked full transitions (the `n+0=n` identity, probability
product law, reciprocal derivative, and the dependent G10 evaluation), then rerun the
same Gold-10 and require the same regression/security gates. No further HML core
change is required by this audit.

## Decision guidance for the Claude/HML-core track

**A. Fix in `hamiltonian-lang` now:** none of the remaining Gold-10 gaps. G06 and
generic G07 quantifier semantics are already repaired at `5688aba`; GAP-0001/0002 use
existing registered checkers. Any new core rule for probability, calculus, or
`n+0=n` would be overfitting and is explicitly rejected by this audit.

**B. Build libraries:** a theorem/evidence library for `n+0=n`; a conditional
probability product theorem under `P(A)>0`; and a calculus library/evidence path for
`d(1/x)/dx=-1/x^2`. Keep exact numeric evaluation in the existing checked evaluator.

**C. Corpus-schema cause:** the single historical `hml_support` field conflated
representability, verification path, and outcome. It made G06’s model construction
ambiguous, treated generic G07 quantifier support as a core gap, and labelled library
work for probability/calculus as core. Phase-B JSON records the three dimensions
separately.

**D. Does 13.04% survive?** No. The post-repair core rate is `0/23 = 0.00%`; the
13.04% figure is not a durable core measure after separating core, certificate,
adapter, and library causes.

**E. Minimum HML changes before another same-Gold-10 rerun:** none beyond the
already-pinned `5688aba` core and the corpus adapters in this report. The remaining
work is trusted library evidence, not HML syntax or kernel semantics.

**F. Dependency order:** (1) preserve pin/read-only guard; (2) retain the checked
certificate boundary; (3) keep the corpus adapters and three-dimensional metadata;
(4) add symbolic identity evidence; (5) add probability-law evidence; (6) add
calculus derivative evidence; (7) rerun the same 23 transitions and security probes;
(8) only then decide on Gold-100.

The full machine-readable transition evidence and security outcomes are in
[PHASE_B_ADAPTED.json](PHASE_B_ADAPTED.json); Phase-A evidence is in
[PHASE_A_PURE_REPIN.md](PHASE_A_PURE_REPIN.md).
