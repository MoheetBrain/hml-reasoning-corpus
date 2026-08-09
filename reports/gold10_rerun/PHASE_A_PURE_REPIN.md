# Gold-10 Phase A — pure repin

Status: complete. This is the pure A/B run against the unchanged corpus renderer.
No canonical trajectory, source problem, state, action, answer, warrant, dependency,
domain, type, or oracle judgment was changed.

## Pins and invariants

| Item | Value |
|---|---|
| Corpus baseline | `467a4866756e6653c1b618a1eed479cda8d5927a` |
| Old HML | `164d1946e91216c093478132caa0d06427259682` |
| New HML | `5688aba18632b65a8709aa1d85577d31a67dba6a` |
| Trajectories | 10 |
| Transitions | 23 |
| Old CoreGapRate | 2/23 = 8.70% |

The pre-repin machine-readable record is
`reports/gold10_rerun/GOLD10_PRE_REPIN_BASELINE.json`. All ten trajectory hashes
and all 23 transition IDs were checked before the repin.

Phase A changed only the `hml_core` gitlink and `schemas/project_metadata.json` in
the project state. The baseline and Phase-A reports are audit records; no mathematical
payload changed.

## Existing Gold-10 suite result

The existing suite returned nonzero with exactly two expected compatibility failures:

1. the old pin guard found the recorded gitlink at `164d194...` while metadata had
   already been updated to `5688aba...`;
2. `tests/test_gold10.py` still hard-coded the old SHA before entering its HML compile
   loop.

This was captured before repairing the corpus harness. It is not a semantic regression.
The same ten HML files were then run directly with the new pinned implementation. All
ten returned exit code 0, with the same behavior as the old baseline: native derivations
remain valid; G06 and G07 remain open because the old renderer emits no new certificate
or quantified-inference statements.

The new HML examples independently passed:

- `certified_underdetermination.hml`: one goal reaches `UNDERDETERMINED`;
- `quantified_inference.hml`: two derivations are `VERIFIED` and the goal is `PROVED`;
- `closed_eval_v1`: exact arithmetic evidence is accepted;
- `definition_unfold_v1`: exact `g(3) = 8` evidence is accepted;
- no certificate leaves a goal `OPEN`/`UNKNOWN` as `UNDERDETERMINED`;
- an unknown checker is rejected by the static registry.

## Full 23-transition Phase-A delta table

`Phase-A classification` describes what is actionable after the repin but before any
corpus adapter work. `CORPUS_ADAPTER_MISSING` means the new HML path exists but the
unchanged renderer does not emit it. `LIBRARY_STILL_MISSING` means the repin did not
add the deliberately out-of-core domain mathematics.

| Transition | Old classification | Phase-A classification | Representation | Verification | Cause |
|---|---|---|---|---|---|
| G01:a0 | current HML | current HML | current | native verified | no change |
| G01:a1 | current HML | current HML | current | native verified | no change |
| G01:a2 | library | adapter missing | current + checked certificate | certificate not emitted | certificate boundary |
| G02:a0 | current HML | current HML | current | native verified | no change |
| G02:a1 | library | adapter missing | current + checked certificate | certificate not emitted | certificate boundary |
| G03:a0 | library | adapter missing | current + checked certificate | certificate not emitted | certificate boundary |
| G03:a1 | library | adapter missing | current + checked certificate | certificate not emitted | certificate boundary |
| G03:a2 | library | adapter missing | current + checked certificate | certificate not emitted | certificate boundary |
| G04:a0 | current HML | current HML | current | native verified | no change |
| G04:a1 | current HML | current HML | current | native verified | no change |
| G05:a0 | current HML | current HML | current | native verified | no change |
| G05:a1 | current HML | current HML | current | native verified | no change |
| G06:a0 | ambiguous | adapter missing | current + certified underdetermination | certificate not emitted | core change present, renderer unused |
| G06:a1 | core missing | adapter missing | current + underdetermined projection | certificate not emitted | core change present, renderer unused |
| G07:a0 | current HML | current HML | current | scope only | no change |
| G07:a1 | core missing | library still missing | quantifier core current; body certificate missing | forall core available; body unsupported | core change present; body library absent |
| G08:a0 | current HML | current HML | current | native verified | no change |
| G08:a1 | current HML | current HML | current | native verified | no change |
| G09:a0 | core missing | library still missing | library required | probability law unsupported | library remains out of core |
| G09:a1 | library | adapter missing | current + checked certificate | certificate not emitted | certificate boundary |
| G10:a0 | current HML | current HML | current | domain check available | no change |
| G10:a1 | library | library still missing | library required | calculus law unsupported | calculus remains out of core |
| G10:a2 | library | library still missing | numeric certificate ready after formula | formula missing | calculus formula remains unavailable |

The JSON companion contains the required old/new reasons and old/new HML behavior for
each row, without collapsing the audit to trajectory-level summaries.

## Phase-A interpretation

The repin itself produces no regression in the 11 previously native transitions. It
does close the semantic *availability* side of GAP-0003 and the generic quantifier
side of GAP-0004, but the unchanged renderer does not use either path. G07 remains
blocked for the exact Gold-10 transition because `n + 0 = n` is not a registered
trusted checker; the new core intentionally does not add an arithmetic theorem.

GAP-0001, GAP-0002, and the numeric portions of G09/G10 now have a checked-certificate
path available in HML. Phase A does not count them as verified because the corpus
renderer has not emitted the evidence. GAP-0005's probability law and GAP-0006's
derivative construction remain library-level blockers.

Phase B may now add only the minimal corpus compatibility adapters and support metadata.
