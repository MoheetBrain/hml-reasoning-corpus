from __future__ import annotations

from typing import Any


def render(manifest: dict[str, Any]) -> str:
    a = manifest["factory_a"]
    b = manifest["factory_b"]
    q = manifest["lean_qualification"]
    p = manifest["performance"]
    authority = manifest["authority"]
    files = manifest["datasets"]
    shortcut = b["audit"]["shortcuts"]
    go_a = "FACTORY_A_READY_FOR_1K" if a["status"] == "PASS" else "FACTORY_A_FIX_FIRST"
    go_b = b["scale_decision"]
    file_rows = "\n".join(f"| `{name}` | `{item['path']}` | {item['records']} | `{item['sha256']}` |" for name, item in files.items())
    failure_rows = "\n".join(f"| `{code}` | {count} |" for code, count in sorted(a["a1_failure_codes"].items()))
    field_rows = "\n".join(f"| `{field}` | `{origin}` | {q['field_recoverable_counts'].get(field, 0):,} |" for field, origin in q["field_provenance"].items())
    return f"""# HMLTN Synthetic Factory V2 — Master Handoff

# 1. EXECUTIVE VERDICT

V2 worked as a contract-separation and narrow semantic-generation project.
Factory A: **{a['status']}** — A1 preserves 100 verifier regression pairs; A2 contains {a['a2_pairs']} clean evidence-conformance pairs.
Factory B: **{b['status']}** — {b['records']} Action Applicability records, {b['audit']['causal_hard_percent']:.1f}% `CAUSAL_HARD`.
Stage100: **{b['stage100_status']}**.
Scale: Factory A may proceed to 1k; Factory B must not scale because one small domain family would merely repeat semantics.
Strongest result: same action plus one actual-domain state difference yields a clean trusted applicability change with no secondary finding.
Strongest remaining flaw: frozen HML does not interpret arbitrary proposition meaning, so Factory B is a narrow domain challenge—not broad mathematical reasoning.
No model was trained. No HML or Claude/FABLE file changed.

# 2. AUTHORITY

| Item | Verified value |
|---|---|
| HML tag | `{authority['hml']['tag']}` |
| HML SHA | `{authority['hml']['sha']}` |
| HML tree | `{authority['hml']['tree']}` |
| corpus SHA | `{authority['corpus']['sha']}` |
| V1 checkpoint | `{authority['corpus']['v1_commit']}` |
| Lean artifact | `{authority['lean']['sha256']}` |
| Lean records | {authority['lean']['records']:,} |
| represented theorems | {q['theorems']:,} |
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

- A1: {a['a1_records']} records / {a['a1_pairs']} pairs across all ten invariant families.
- A2: {a['a2_records']} records / {a['a2_pairs']} pairs; {a['a2_gold_percent']:.1f}% clean learning-conformance records.
- Distribution: `CHALLENGE_BALANCED`, not source-natural.

| A1 rejection code | Count |
|---|---:|
{failure_rows}

# 6. FACTORY B

Factory B builds fresh representation-neutral applicability records from the frozen, executable versioned domain lattice. It never asks HML to understand opaque proposition strings.

- 100 domain-lattice records: 50 applicable, 50 not applicable across two neutral contexts.
- Labels: `APPLICABLE`, `NOT_APPLICABLE`; unresolved is preserved and excluded from Gold rather than converted.
- Same operation (`DERIVE`) appears on both labels. State and action remain well formed; rejected oracle transitions have exactly one `TYPE_DOMAIN` finding.
- Nearby positive alternatives: {b['audit']['valid_alternatives']}.
- Gold is challenge-balanced and has no TRAIN status; it must not be described as a natural source distribution.

# 7. CONTRADICTORY-SUPERVISION AUDIT

Factory A conflicting learner inputs: {a['contradictions']}.
Factory B conflicting learner inputs: {b['audit']['contradictions']['conflicting_input_count']}.
Factory B unique learner inputs: {b['audit']['contradictions']['unique_inputs']} / {b['records']}.
Promotion requires and achieves zero conflicting labels for identical learner-visible inputs.

# 8. SHORTCUT AUDIT

| Baseline | Accuracy |
|---|---:|
| sentinel rule | {shortcut['sentinel_rule_accuracy']:.1%} |
| mutation family only | {shortcut['mutation_only_accuracy']:.1%} |
| changed field only | {shortcut['changed_field_accuracy']:.1%} |
| action family only | {shortcut['action_family_accuracy']:.1%} |
| best in-sample text-length threshold | {shortcut['best_in_sample_length_threshold_accuracy']:.1%} |
| lexical Naive Bayes, neighborhood holdout | {shortcut['lexical_naive_bayes_group_holdout_accuracy']:.1%} |
| full frozen semantic oracle | {shortcut['full_frozen_semantic_oracle_accuracy']:.1%} |

Sentinel occurrences in Factory-B Gold: {shortcut['sentinel_occurrences']}. Mutation-only features exclude labels and audit prose. The full oracle's advantage is relational: actual domain versus required domain.

# 9. CAUSAL-HARD AUDIT

| Class | Count |
|---|---:|
| `CAUSAL_HARD` | {b['audit']['causal_classes'].get('CAUSAL_HARD', 0)} |
| `STRUCTURAL_SHORTCUT` | {b['audit']['causal_classes'].get('STRUCTURAL_SHORTCUT', 0)} |
| `AMBIGUOUS` | {b['audit']['causal_classes'].get('AMBIGUOUS', 0)} |
| `NON_CAUSAL` | {b['audit']['causal_classes'].get('NON_CAUSAL', 0)} |

Representative pair: an `Integer` input inhabits `Real`, while a `Real` input does not inhabit `Integer`; the action's required domain supplies the context. This is current versioned HML lattice data, not a classical operation invented by the generator. Scope was explicitly rejected from Factory-B Gold: output scope lives only in proposed `S_after`, so it belongs to `TRANSITION_CONFORMANCE`; treating it as `(S,a)` applicability produced contradictory supervision during development.

# 10. VALID ALTERNATIVES

There are {b['audit']['valid_alternatives']} additional applicable members in neighborhoods that already contain an applicable anchor. They vary the actual domain while retaining the candidate action contract. This prevents “synthetic variant means bad” supervision.

# 11. SPLIT/LEAKAGE AUDIT

Factory B is a constructed `CHALLENGE` set with no parent theorem and is not TRAIN data. Factory A inherits every DEV/FINAL source split from its parent fixture. Theorem overlap counts are `{b['audit']['leakage']['overlap_counts']}` for Factory B and `{a['leakage']['overlap_counts']}` for Factory A. No DEV/FINAL descendant enters TRAIN.

# 12. LEAN QUALIFICATION CENSUS

All {q['records_scanned']:,} rows were streamed and checked field by field:

| Contract | Eligible | Exact interpretation |
|---|---:|---|
| `ACTION_APPLICABILITY` | {q['eligible']['ACTION_APPLICABILITY']:,} | observed successful Lean tactic positives only; no certified counterfactual negatives |
| `TRANSITION_CONFORMANCE` | {q['eligible']['TRANSITION_CONFORMANCE']:,} | Lean-native before/tactic/after trace, not an HML SemanticState transition |
| `EVIDENCE_SUFFICIENCY` | {q['eligible']['EVIDENCE_SUFFICIENCY']:,} | no explicit evidence/certificate learner input exists |

| Adapter field | Provenance | Recoverable rows |
|---|---|---:|
{field_rows}

The census never infers dependencies, typed HML arguments, evidence, preconditions, obligations or scope. `LLM_GUESS=0`, `HEURISTIC_GUESS=0`. Theorem split overlap count: {q['theorem_split_overlap_count']}.
The leakage split is the project theorem-level mapping (seed 20260811): TRAIN {q['split_record_counts']['TRAIN']:,}, DEV {q['split_record_counts']['DEV']:,}, FINAL {q['split_record_counts']['FINAL']:,}. LeanDojo's raw train/val/test field is retained only as source metadata.

# 13. PERFORMANCE

| Stage | Rate | Workers | CPU/RAM note |
|---|---:|---:|---|
| Lean qualification | {q['performance']['records_per_second']:.1f} records/s | 1 | streaming one record |
| Factory-B mutation + audit + verification | {p['full_pipeline_records_per_second']:.1f} accepted Gold records/s | 1 | peak RSS {p['full_pipeline_peak_rss_kib']} KiB |
| isolated frozen verifier batch | {p['verifier']['verifications_per_second']:.1f} verifications/s | {p['verifier']['workers']} | {p['verifier']['aggregate_cpu_percent']:.1f}% aggregate CPU; peak child RSS {p['verifier']['peak_child_rss_kib']} KiB |

Eight workers remain the verifier default. Qualification and full-pipeline rates are reported separately; V1 verifier throughput is not presented as end-to-end speed.

# 14. DATASET MANIFESTS

| Dataset | Path | Records | SHA-256 |
|---|---|---:|---|
{file_rows}

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

- **{go_a}** — scale A2 only with the same sentinel, collision and single-finding gates.
- **{go_b}** — Stage100 passes, but 1k would duplicate a single small relation. Add a second genuinely certified applicability family through a trusted backend; do not smuggle scope or classical operations into `(S,a)` labels.

# 18. NEXT ATOMIC TASK

Build a runtime Lean evidence-attestation adapter that replays a held-out sample under the pinned Lean/mathlib environment and emits unforgeable before/tactic/after certificates; do not generate Lean negatives until that adapter passes.
"""
