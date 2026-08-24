# State sufficiency report

## Method

The audit used 235,265 transitions from 59,982 Lean theorem parents after excluding both sealed fresh holdouts. No `FRESH_FINAL_A/B` row entered discovery statistics. Deterministic signatures were computed from the exact current state and from an identifier/number-normalized structural state. The target is the recorded next tactic family; this is an observational sufficiency diagnostic, not a uniqueness claim about valid Lean actions.

## Aliasing

- Exact current-state hashes: 233,467; ambiguous exact clusters: 1,050, covering 2,122 rows.
- Structural current-state signatures: 231,656; ambiguous clusters: 1,598, covering 3,297 rows.
- H(next tactic family | structural current state): 0.0141 bits.
- H(next tactic family | structural state, last 4 successful tactic families): 0.0008 bits.
- Observed reduction: 0.0133 bits.

## Interpretation

Observational evidence that recent successful trajectory history reduces ambiguity beyond a deterministic structural current-state signature. This supports testing bounded successful history, but it does not prove that identical Lean states require a unique action or that history is causally necessary: formal proofs permit multiple valid tactics and the corpus contains one successful trace per example. The 200 highest-evidence deterministic clusters are saved separately with hashes, action-family distributions and representative IDs; no holdout examples are included.

## Candidate missing variables

Recent successful actions and their state deltas reduce recorded-action ambiguity beyond the tested structural signature and are available online before the next action. Explicit goal queues, local declaration dependencies and case identity are already present or derivable from the current Lean state; they test semantic accessibility/organization rather than missing raw information. Failed-route memory, branch parent/coverage, goal genealogy and strategy/lemma roles are absent from passive source and are not admitted.
