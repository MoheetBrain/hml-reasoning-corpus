# Pre-registered analyses for EXP_REP_VALIDITY_V1

**Written before any Stage 1 result exists.** Committed alongside the harness that performs
them, so the axes, the binning, the statistic and the direction of each hypothesis are fixed
in code rather than chosen once numbers are visible. §19 asks for this explicitly: *predefine
these analyses; do not invent them after seeing results.*

Nothing below may be revised after the first GPU run. If an axis turns out to be uninformative
it stays in the report as uninformative.

## 1. Primary comparison

**Quantity.** Paired difference in accuracy between `R_HML` and the best-performing control
arm, on each evaluation split, over items sharing a semantic id.

**Pairing unit is the parent theorem, not the row.** The three items derived from one parent
share the entire state and differ in one mutation; treating them as three independent
observations would understate every interval. The bootstrap resamples parents and carries
their siblings with them.

**Reported.** Raw delta, 95% bootstrap CI (10,000 resamples), McNemar discordant-pair counts
with an exact two-sided binomial p, macro-F1, cross-entropy, bits per example, and the
`StateInformationGain = H(Y) - H(Y|R)` for every arm.

**Decision rule.** An interval that excludes zero is a representation effect. An interval that
spans zero is reported as "this dataset cannot resolve it", never as "no difference".

## 2. The control the primary comparison is read against

Not the class prior. A bag-of-words logistic regression with no language model reaches
macro-F1 ≈ 0.68 on this task (per-arm spread 0.021, measured on CPU before any GPU time).

`probe_minus_own_bag_of_words_macro_f1` is therefore reported per arm per split, and is the
number that decides whether Stage 1 says anything about the model at all. An arm that beats
the class prior but not its own lexical control has shown the *task* carries signal, not that
the *model* reads mathematical state.

## 3. Complexity interactions (§19)

**Hypothesis, stated in advance and in one direction.** The interesting prediction is not a
constant advantage. It is that the advantage **grows with semantic complexity**:

```
interaction = (HML − best control) in the top tercile
            − (HML − best control) in the bottom tercile
```

positive, with a bootstrap CI over parents excluding zero.

A constant advantage across bins is a weaker but still real result. A *shrinking* advantage
is evidence against the structural reading and for a familiarity or verbosity explanation.

### Axes, fixed in `harness/interactions.py`

| axis | binning | status in this corpus |
|---|---|---|
| `binder_depth` (bracket nesting + quantifiers in the goal) | terciles | testable |
| `max_dependency_depth` | terciles | testable, but **narrow**: spans 0–6, top decile 3 |
| `n_claims` (state size) | terciles | testable; strongest axis, spans 2–81 |
| `n_cited` (premises the action rests on) | terciles | testable |
| `n_dependency_edges` | terciles | testable |
| `goal_chars`, `state_chars` | terciles | testable |
| `quantifiers` | terciles | often degenerate — 0 for most items |
| `has_branch` | false vs true | testable |
| `discharges_goal` | false vs true | testable |
| `domain_area` (Mathlib area) | per group | reported per group; no ordering, so no interaction test |
| `token_length` | terciles of the **HML** render's token count | testable |
| number of obligations | — | **degenerate: 0 for every item.** Recorded Lean tactic states carry no proof debt. Reported as untestable rather than stratified into a constant. |

A tail bin with fewer than 30 items is reported but **not** tested: a bootstrap over a handful
of parents yields an interval wide enough to be uninformative and narrow enough to be mistaken
for a finding.

## 4. OOD splits and what each is for

| split | tests | note |
|---|---|---|
| `test_iid` | in-distribution generalisation | the headline number |
| `ood_alpha_rename` | unseen binder spellings | **also the memorisation control.** Every state is recorded Mathlib and every model under test has read Mathlib; the Lean-like arm resembles the source most. An arm that wins on `test_iid` but not here was retrieving, not reading. |
| `ood_binder_depth` | deeper quantifier/bracket structure | training excludes the top decile |
| `ood_dependency_depth` | longer premise chains | narrow axis; interpret cautiously |
| `ood_state_size` | larger states | training excludes the top decile |
| `ood_composition` | two mutation families never seen in training | familiar primitives, unseen combination |
| `ood_domain` | CategoryTheory and NumberTheory, withheld entirely | unseen mathematics |

## 5. What would falsify the HML thesis

Stated in advance so the result cannot be reinterpreted afterwards:

- **HML ≈ controls on every split and every axis.** Representation is not a causal capability
  variable at this scale and task. §14B: run the MLP probe, then stop.
- **HML < controls with an interval excluding zero.** §14D: preserve the result, do not
  redesign the language to chase it.
- **All arms ≈ their own bag-of-words control.** The frozen model is not reading state through
  any of these surfaces. §14A: stop the GPU and diagnose the interface, not the language.
- **The Lean-like arm wins on `test_iid` but that win vanishes under `ood_alpha_rename`.**
  The effect was Mathlib familiarity, and the correct reading is about pretraining exposure,
  not notation.

## 6. What is explicitly *not* pre-registered

Anything not listed above is exploratory and must be labelled as such in any write-up. In
particular: per-mutation-family breakdowns, per-error-class breakdowns and layer-wise probe
comparisons are diagnostics, not tests, and no claim rests on them.
