# HML50K data audit

Verdict: `HML50K_READY`.

- 56,000 canonical worked transitions: 50,000 TRAIN, 3,000 DEV, 3,000 FINAL.
- 56,000 paired rows per view for action selection, delta prediction, and continuation;
  112,000 paired judge rows per view because each state has one FORMAL_TRACE and one
  UNRESOLVED proposal.
- 56,000 exact raw/canonical trace matches and 56,000 premise lists recovered.
- 16,950 distinct parent theorems; 14,080 complete source trajectories after all exclusions,
  including 5,897 complete multi-step trajectories.
- 0 duplicate IDs, 0 cross-split near-signature matches, 0 cross-split parent overlap.
- 0 old VNext/autopsy parents in FINAL; FINAL contains 3,000 records from 888 official-test
  parent theorems.
- 112,000 HML state round-trips during construction; an independent audit later made
  112,000 state parity comparisons, 224,000 action-envelope comparisons, and 56,000
  candidate-order comparisons.

The structural-stress reference subset contains 5,000 unchanged canonical records, 4,358
of them in the highest frozen complexity bin. It does not manufacture branch, candidate
lifecycle, or obligation semantics absent from the source.

Machine results are under `audits/`; five manually inspected FINAL records across depth
strata are recorded in `audits/manual_inspection.json`.
