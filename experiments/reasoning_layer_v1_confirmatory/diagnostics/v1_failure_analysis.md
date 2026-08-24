# V1 failure analysis

Final verdict: `V1_SEMANTIC_COMPRESSION_FAILED`. RAW−BASE Top-1 is +1.13pp with 95% CI [+0.31, +2.04]pp. SEMANTIC−RAW is -0.70pp with 95% CI [-1.64, +0.16]pp.

## Causal answers

1. **Did RAW_HISTORY beat BASE? Yes.** The gain is +1.13pp and its clustered CI
   [+0.31, +2.04]pp excludes zero.
2. **Did SEMANTIC lose information relative to RAW? Yes.** Top-1 is 0.70pp lower;
   RAW-correct/SEMANTIC-wrong patterns number 103 versus 82 in the reverse direction.
3. **Which modules distinguish the asymmetric wins?** HISTORY is the clearest observed
   split: SEMANTIC−RAW is -1.20pp on 2,243 history-present rows (CI [-2.31, -0.13]pp)
   versus +0.79pp on 757 history-absent rows (CI [-0.79, +2.51]pp). Exact loss profiles
   for both asymmetric sets are in `information_loss.json`.
4. **Are DEPENDENCIES associated with regressions? Weakly, not causally.** SEMANTIC−RAW
   is -0.81pp when dependencies are present and +0.34pp when absent, but both CIs include
   zero and the strata differ in many other ways.
5. **Does HISTORY help at later trajectory positions? Not consistently.** SEMANTIC−RAW
   is -3.16pp at positions 4–7 (CI [-5.42, -0.92]pp), -0.50pp at 8–15, and +2.56pp at
   16+ with a CI spanning zero. RAW's overall history gain is credible, but no monotonic
   late-position semantic advantage appears.
6. **Does BRANCH_SCOPE help case-labelled states? No observed differential benefit.**
   SEMANTIC−RAW is -0.65pp with a case label and -0.74pp without one; both CIs span zero.
7. **Does GOALS help multi-goal states? Inconclusive.** Only 16/3,000 rows have multiple
   goals. The 14-row two-to-three-goal stratum is -7.14pp with a very wide CI; GOALS is
   present on every row, so no goals-absent control exists.
8. **Does semantic compression fail more as depth increases? No monotonic trend.** It is
   negative at depths 2–10, zero at 11–20, and +3.78pp in the small 21+ stratum.
9. **Did RAW gain from exact prior tactic text? Plausibly.** RAW-only rows average 2.43
   omitted exact tactic arguments over 2.63 history events; V1 retains only tactic family.
   This is an association, not an isolated ablation.
10. **Did RAW carry useful prior-state detail discarded by recent deltas? Plausibly.**
    84.5% of RAW-only rows have prior intermediate proposition/state content that V1
    reduces to coarse deltas, versus 73.2% of semantic-only rows.
11. **Are recent deltas too lossy? The evidence points that way.** They retain names and
    counts but omit exact propositions; the asymmetric-win inventory is directionally
    consistent with that omission.
12. **Is the four-event window visibly insufficient? Not established.** Window saturation
    is modestly enriched in RAW-only rows (49.5%) versus semantic-only rows (45.1%) and all
    rows (40.1%), but RAW and SEMANTIC share the same four-event horizon, so this experiment
    cannot identify a longer-window effect.
13. **What remains missing evidence?** Failed-route/search memory, goal genealogy,
    strategy state, lemma/invariant role, and full branch-parent/coverage structure remain
    `MISSING_EVIDENCE` candidates only. Successful passive traces do not establish them.

## Dominant information-loss mechanism

V1 reduces exact prior tactic text to tactic family and exact prior states/propositions to coarse deltas. RAW-only loss profile: `{"branch_ancestry_available_in_raw": 0.5048543689320388, "exact_prior_hypotheses_omitted": 21.25242718446602, "exact_prior_state_content_omitted": 0.8446601941747572, "exact_prior_targets_omitted": 1.8737864077669903, "exact_tactic_arguments_omitted": 2.4271844660194173, "history_events": 2.6310679611650487, "prior_intermediate_proposition_content_omitted": 0.8446601941747572, "tactic_retained_as_family_only": 0.8446601941747572, "window_saturated": 0.49514563106796117}`.

## V2 decision

Evidence threshold for proposing one V2 is **met**. This file does not alter V1 and FINAL_B remains sealed. A V2, if separately authorized, must cite these FINAL_A row counts and preserve only the specific exact-history content associated with RAW-only wins.
