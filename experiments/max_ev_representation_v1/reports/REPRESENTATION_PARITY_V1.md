# REPRESENTATION_PARITY_V1

**Parity: PASS. Leakage: PASS. Training is not blocked.**

Dataset `DATASET_V1-1.0.0`, 5619 rows, four arms, task `ACTION_VALIDITY`.
Labels come from `hamiltonian_lang.semantic_state.verify.verify_replay` — the frozen verifier, never a judge.

## 1. Parity

Every arm's rendered text is read back and the recovered objects compared. Nothing here is
asserted from the generator's intent; it is measured on the bytes the model will receive.

| check | result |
|---|---|
| self-fidelity — re-render reproduces the stored bytes exactly | HML 5619 / TYPED_AST 5619 / LEANLIKE 5619 / STRUCTURED_ENGLISH 5619 of 5619 |
| cross-arm identity — all four recover the same object | **5619 / 5619** |
| label preserved — re-verified transition still carries its label | **5619 / 5619** |
| §5 properties failing on any row | **none** |

Properties checked field by field (16): action_envelope, assumptions_and_facts, binder_identity, branches, candidates, constraints, dependencies, epistemic_state, evidence_references, goals, object_identity, obligations, preconditions, scope, types, warrants.

Record **order** is excluded from the comparison and nothing else is. A `SemanticState` maps
id to record, the verifier never reads order, and the frozen HML view emits its own order for
readability — §5's "up to representation-only differences" is exactly this case. Every field
of every record still has to match exactly, and does.

## 2. Leakage

| channel | result |
|---|---|
| answer-word mutual information | {'VALID': 0.0} bits |
| mutation-family name in any render | **none** |
| source-ID markers (file path, theorem, hashes) | **none** |
| operation-name mutual information | 0.0 bits (operations present: ['LEAN_TACTIC']) |
| Mathlib-area mutual information | 0.0 bits |
| label prior entropy | 1.585 bits, counts {'VALID': 1873, 'INVALID': 1873, 'UNRESOLVED': 1873} |

Operation and area carry **0.000 bits** because of how items are built, not because of
filtering: each parent contributes exactly one VALID, one INVALID and one UNRESOLVED sibling,
so every property of the parent is constant across the three labels. That construction was
chosen after measuring the alternative — in `vnext_10k` the verifier's natural verdict is
predicted almost perfectly by the operation name alone (LEAN_TACTIC 4000/4000 VALID,
SOURCE_DERIVATION 2000/2000 UNRESOLVED, OPEN_BRANCH 61/61 INVALID). A dataset drawn from that
distribution would have measured a token lookup.

### Highest-information single tokens

| arm | top tokens by I(present; label), bits |
|---|---|
| R_HML | `OPEN` 0.08158, `DERIVED` 0.04903, `True` 0.02625, `VERIFIED` 0.01501, `UNKNOWN` 0.00813 |
| R_TYPED_AST | `OPEN` 0.08158, `DERIVED` 0.04903, `True` 0.02625, `VERIFIED` 0.01501, `UNKNOWN` 0.00813 |
| R_LEANLIKE | `OPEN` 0.08158, `DERIVED` 0.04903, `True` 0.02625, `VERIFIED` 0.01501, `UNKNOWN` 0.00813 |
| R_STRUCTURED_ENGLISH | `OPEN` 0.08158, `DERIVED` 0.04903, `True` 0.02625, `VERIFIED` 0.01501, `UNKNOWN` 0.00813 |

Against a label entropy of 1.585 bits, the largest single-token share is
0.08158 bits
(~5%).
Two tokens that previously dominated were repaired rather than tolerated: `UNKNOWN` fell from
**0.918 bits to 0.00813**
and `VALID` from **0.231 to 0.000**, by giving every item — of every label — one uncited
UNKNOWN claim and one uncited VALID attestation. That is not concealment: the verifier's
unknown collection is dependency-scoped (D-049), so an uncited unknown genuinely does not
make a transition UNRESOLVED, and the repair converts "spot the word" into "check which
record carries it", which is the rule the verifier actually implements.

### Surface statistics

A decision stump fitted on each surface statistic — threshold and labels both chosen on the
same data, so these *over*-state what a real classifier could do:

| arm | characters | lines | alphabetic fraction | non-ASCII |
|---|---|---|---|---|
| R_HML | 0.3406 | 0.3399 | 0.3437 | 0.3376 |
| R_TYPED_AST | 0.3397 | 0.3429 | 0.3445 | 0.3362 |
| R_LEANLIKE | 0.3403 | 0.3476 | 0.3449 | 0.3376 |
| R_STRUCTURED_ENGLISH | 0.341 | 0.3463 | 0.3412 | 0.3376 |

Majority-class baseline is 0.3333.
Nothing exceeds it by more than ~1.4pp, so a probe cannot succeed on length or character
composition — which matters here specifically, because a linear probe on pooled embeddings is
exactly the kind of model that would otherwise do so.

## 3. The bound this audit cannot give you

Single-token mutual information is not the lexical ceiling. A linear combination of many
weakly-informative tokens can be far stronger than any one of them, and only a fitted lexical
model measures that. Measured on the full dataset with no language model involved, a
bag-of-words multinomial logistic regression reaches **macro-F1 ≈ 0.68** (per-arm spread
0.021, so the arms are lexically well matched).

That, not the 0.333 class prior, is the bar Stage 1 has to clear. It is carried into the
harness as a per-arm control and reported as `probe_minus_own_bag_of_words_macro_f1`, and it
is part of the headroom gate: a task can be unsaturated for the model and still be solved by
counting tokens.

## 4. Arm length asymmetry — recorded, not corrected

| arm | mean chars | p95 | p99 | max |
|---|---:|---:|---:|---:|
| R_HML | 3843 | 7163 | 9731 | 16463 |
| R_TYPED_AST | 5075 | 8837 | 12693 | 18853 |
| R_LEANLIKE | 2567 | 4502 | 6200 | 8861 |
| R_STRUCTURED_ENGLISH | 4266 | 7372 | 10121 | 15302 |

The arms differ by up to 2x in length. That is an intrinsic property of the notations, not an
instrumentation defect, so it is measured and reported rather than equalised — padding a
terse notation to match a verbose one would destroy the thing under test. Two consequences are
handled explicitly: the context is 8,192 tokens so no arm is truncated (truncation is counted
per arm in the run manifest), and token count is a predefined interaction term in §19.

