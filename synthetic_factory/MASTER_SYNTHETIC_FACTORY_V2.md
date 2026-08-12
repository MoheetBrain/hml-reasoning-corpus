# HMLTN Synthetic Factory V2 — Master Handoff

# 1. EXECUTIVE VERDICT

V2 worked as a contract-separation and narrow semantic-generation project.
Factory A: **PASS** — A1 preserves 100 verifier regression pairs; A2 contains 20 clean evidence-conformance pairs.
Factory B: **PASS** — 100 Action Applicability records, 100.0% `CAUSAL_HARD`.
Stage100: **PASS**.
Scale: Factory A may proceed to 1k; Factory B must not scale because one small domain family would merely repeat semantics.
Strongest result: same action plus one actual-domain state difference yields a clean trusted applicability change with no secondary finding.
Strongest remaining flaw: frozen HML does not interpret arbitrary proposition meaning, so Factory B is a narrow domain challenge—not broad mathematical reasoning.
No model was trained. No HML or Claude/FABLE file changed.

# 2. AUTHORITY

| Item | Verified value |
|---|---|
| HML tag | `hml-semantic-pre-gemma-v1` |
| HML SHA | `84bf9897689b0ed78a2caaefc1db850d49b81260` |
| HML tree | `a81c8f414f0159a7a55dec5ddddbc5a955185d9d` |
| corpus SHA | `9d67e54450b9db897ee2ed20ec2e4cbbc16a3780` |
| V1 checkpoint | `820544372f092392321f5b93e4a14f244fd24272` |
| Lean artifact | `8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869` |
| Lean records | 241,265 |
| represented theorems | 61,542 |
| frozen HML | read-only, Git-clean, zero writable files |

# 3. V1 FORENSIC LESSON

V1 mechanically accepted 100 pairs but forensic review found 20 semantic, 60 structural and 20 ambiguous. It proved the verifier harness, provenance, determinism and multiprocessing. It also proved that a changed verifier verdict is not automatically a mathematical causal negative: missing sentinel IDs, direct status contradictions and multi-failure frame drift create learner shortcuts or contradictory task supervision.

# 4. TASK-CONTRACT SEPARATION

- `ACTION_APPLICABILITY`: learner sees `(S_before, candidate_action)` and predicts whether the action may be applied.
- `TRANSITION_CONFORMANCE`: learner sees `(S_before, action, proposed_S_after)` and predicts whether declared effects and frame materialise exactly.
- `EVIDENCE_SUFFICIENCY`: learner additionally sees evidence and predicts whether it licenses the transition or promotion.

Every record declares exactly one contract. Canonical learner-input hashes are computed from only that contract's visible fields. Factory B contains only `ACTION_APPLICABILITY`; A2 contains only `EVIDENCE_SUFFICIENCY`. A1 keeps contract-separated regression probes and is not promoted as one shared binary label space.

# 5. FACTORY A

Factory A consumes the frozen V1 transition pairs and emits diagnostic records with precise `HML_TRANSITION_ACCEPTED` / `HML_TRANSITION_REJECTED` labels, failure stage, failure code and invariant. A1 retains obvious sentinels and direct contradictions strictly as verifier QA. A2 admits only branch-coverage and candidate-constraint certificate mutations: both sides import, no sentinel appears, and every rejected example has exactly one intended finding.

- A1: 200 records / 100 pairs across all ten invariant families.
- A2: 40 records / 20 pairs; 100.0% clean learning-conformance records.
- Distribution: `CHALLENGE_BALANCED`, not source-natural.

| A1 rejection code | Count |
|---|---:|
| `CANDIDATE_PROMOTION` | 10 |
| `DEPENDENCY_VIOLATION` | 10 |
| `EPISTEMIC_PROMOTION` | 10 |
| `FALSE_GOAL_DISCHARGE` | 10 |
| `INVALID_BRANCH_JOIN` | 10 |
| `OBLIGATION_DROP` | 10 |
| `PRECONDITION_VIOLATION` | 10 |
| `SCOPE_LEAK` | 10 |
| `TYPE_OR_DOMAIN_MISMATCH` | 10 |
| `WARRANT_MISMATCH` | 10 |

# 6. FACTORY B

Factory B builds fresh representation-neutral applicability records from the frozen, executable versioned domain lattice. It never asks HML to understand opaque proposition strings.

- 100 domain-lattice records: 50 applicable, 50 not applicable across two neutral contexts.
- Labels: `APPLICABLE`, `NOT_APPLICABLE`; unresolved is preserved and excluded from Gold rather than converted.
- Same operation (`DERIVE`) appears on both labels. State and action remain well formed; rejected oracle transitions have exactly one `TYPE_DOMAIN` finding.
- Nearby positive alternatives: 30.
- Gold is challenge-balanced and has no TRAIN status; it must not be described as a natural source distribution.

# 7. CONTRADICTORY-SUPERVISION AUDIT

Factory A conflicting learner inputs: 0.
Factory B conflicting learner inputs: 0.
Factory B unique learner inputs: 100 / 100.
Promotion requires and achieves zero conflicting labels for identical learner-visible inputs.

# 8. SHORTCUT AUDIT

| Baseline | Accuracy |
|---|---:|
| sentinel rule | 50.0% |
| mutation family only | 50.0% |
| changed field only | 50.0% |
| action family only | 50.0% |
| best in-sample text-length threshold | 68.0% |
| lexical Naive Bayes, neighborhood holdout | 44.0% |
| full frozen semantic oracle | 100.0% |

Sentinel occurrences in Factory-B Gold: 0. Mutation-only features exclude labels and audit prose. The full oracle's advantage is relational: actual domain versus required domain.

# 9. CAUSAL-HARD AUDIT

| Class | Count |
|---|---:|
| `CAUSAL_HARD` | 100 |
| `STRUCTURAL_SHORTCUT` | 0 |
| `AMBIGUOUS` | 0 |
| `NON_CAUSAL` | 0 |

Representative pair: an `Integer` input inhabits `Real`, while a `Real` input does not inhabit `Integer`; the action's required domain supplies the context. This is current versioned HML lattice data, not a classical operation invented by the generator. Scope was explicitly rejected from Factory-B Gold: output scope lives only in proposed `S_after`, so it belongs to `TRANSITION_CONFORMANCE`; treating it as `(S,a)` applicability produced contradictory supervision during development.

# 10. VALID ALTERNATIVES

There are 30 additional applicable members in neighborhoods that already contain an applicable anchor. They vary the actual domain while retaining the candidate action contract. This prevents “synthetic variant means bad” supervision.

# 11. SPLIT/LEAKAGE AUDIT

Factory B is a constructed `CHALLENGE` set with no parent theorem and is not TRAIN data. Factory A inherits every DEV/FINAL source split from its parent fixture. Theorem overlap counts are `{'TRAIN_INTERSECT_DEV': 0, 'TRAIN_INTERSECT_FINAL': 0, 'DEV_INTERSECT_FINAL': 0}` for Factory B and `{'TRAIN_INTERSECT_DEV': 0, 'TRAIN_INTERSECT_FINAL': 0, 'DEV_INTERSECT_FINAL': 0}` for Factory A. No DEV/FINAL descendant enters TRAIN.

# 12. LEAN QUALIFICATION CENSUS

All 241,265 rows were streamed and checked field by field:

| Contract | Eligible | Exact interpretation |
|---|---:|---|
| `ACTION_APPLICABILITY` | 241,265 | observed successful Lean tactic positives only; no certified counterfactual negatives |
| `TRANSITION_CONFORMANCE` | 241,265 | Lean-native before/tactic/after trace, not an HML SemanticState transition |
| `EVIDENCE_SUFFICIENCY` | 0 | no explicit evidence/certificate learner input exists |

| Adapter field | Provenance | Recoverable rows |
|---|---|---:|
| `state_before` | `DIRECT_SOURCE` | 241,265 |
| `candidate_action` | `DIRECT_SOURCE` | 241,265 |
| `state_after` | `DIRECT_SOURCE` | 241,265 |
| `formal_backend_trace` | `FORMAL_BACKEND` | 241,265 |
| `dependencies` | `NOT_RECOVERABLE` | 0 |
| `typed_action_arguments` | `NOT_RECOVERABLE` | 0 |
| `evidence` | `NOT_RECOVERABLE` | 0 |
| `preconditions` | `NOT_RECOVERABLE` | 0 |
| `obligations` | `NOT_RECOVERABLE` | 0 |
| `scope` | `NOT_RECOVERABLE` | 0 |

The census never infers dependencies, typed HML arguments, evidence, preconditions, obligations or scope. `LLM_GUESS=0`, `HEURISTIC_GUESS=0`. Theorem split overlap count: 0.
The leakage split is the project theorem-level mapping (seed 20260811): TRAIN 192,882, DEV 24,067, FINAL 24,316. LeanDojo's raw train/val/test field is retained only as source metadata.

# 13. PERFORMANCE

| Stage | Rate | Workers | CPU/RAM note |
|---|---:|---:|---|
| Lean qualification | 63773.5 records/s | 1 | streaming one record |
| Factory-B mutation + audit + verification | 952.3 accepted Gold records/s | 1 | peak RSS 36092 KiB |
| isolated frozen verifier batch | 43608.7 verifications/s | 8 | 335.5% aggregate CPU; peak child RSS 39712 KiB |

Eight workers remain the verifier default. Qualification and full-pipeline rates are reported separately; V1 verifier throughput is not presented as end-to-end speed.

# 14. DATASET MANIFESTS

| Dataset | Path | Records | SHA-256 |
|---|---|---:|---|
| `factory_a1` | `synthetic_factory_v2/data/factory_a/a1_regression.jsonl` | 200 | `85d8267891e6ef5bfb18cc0764af2859fc59cf6ed820347bcb0bbfa8b90c1555` |
| `factory_a2` | `synthetic_factory_v2/data/factory_a/a2_learning.jsonl` | 40 | `6e7db669d18666e2f0ecd88f8d7f43bd11fa2a4c3af9a9aa8965a4da6749d0ef` |
| `factory_b_gold_stage100` | `synthetic_factory_v2/data/factory_b/gold_stage100.jsonl` | 100 | `d2f59932e28d3e808c83d2529086a4c01931b09ddc9cc0c08488186bee525b47` |

Canonical records are representation-neutral objects. HML and AST renderings remain downstream views and are not embedded as the source of truth.

# 15. SEMANTIC LIMITATIONS

- Opaque proposition bodies prevent certification of division-by-zero, radical sign, parity, determinant and similar classical counterfactuals without a trusted library/backend.
- The Lean export supplies successful positive actions but no executable attestation envelope in this workspace and no certified negative mutations.
- Candidate and branch certificates check recorded identity coverage; they do not independently prove arbitrary source mathematics.
- Goal creation remains unrepresentable for 18,315 Lean transitions.
- Factory B currently measures domain applicability only. Scope is transition conformance under the current action schema. Generalising this result would be overclaiming.

# 16. FABLE HANDOFF

Consume Factory A A1 only for verifier regression/error diagnosis. A2 may be used for evidence-sufficiency learning, keeping its contract field and inherited split. Consume Factory B only for `(S,a) -> applicable?` challenge experiments, comparing renderings generated from the same canonical record. Never merge Factory A/B labels, never move DEV/FINAL descendants into TRAIN, and never treat `HML_FRAME_ACCEPTED` as an independent proof of opaque source mathematics.

# 17. GO / NO-GO

- **FACTORY_A_READY_FOR_1K** — scale A2 only with the same sentinel, collision and single-finding gates.
- **FACTORY_B_FIX_FIRST** — Stage100 passes, but 1k would duplicate a single small relation. Add a second genuinely certified applicability family through a trusted backend; do not smuggle scope or classical operations into `(S,a)` labels.

# 18. NEXT ATOMIC TASK

Build a runtime Lean evidence-attestation adapter that replays a held-out sample under the pinned Lean/mathlib environment and emits unforgeable before/tactic/after certificates; do not generate Lean negatives until that adapter passes.
