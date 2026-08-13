# FABLE VNext 10k Handoff — D1/D2 Patched

FABLE must re-attest this release before training:

- Export data/implementation commit: `a2f992a6d474638814a1f1f7809f4015db3894c5`
- Canonical 10k semantic-data authority: `09521ae992af5ca583a346da66c93d986e709386`
- HML semantic authority: `68178f07784d2a17a9aed9c4dedbea9c740c97a0`
- Translation contract: `vnext-translation-contract-1.0.0`
- FABLE finding/attestation: `435571e`
- Manifest SHA-256: `77dfee09aaad6616f79057383be6e9c699b95db5e12ddec19dcfb0f9791a9af1`

The canonical 10,000 transitions, record ids, source assignments, splits, task
eligibility, and snapshot membership are unchanged. This release changes only
the model-facing projection contract and its audits.

## Authoritative files

- Manifest: `data/vnext_10k/manifest.json`
- Full audit records: `data/vnext_10k/full_audit_records.jsonl.gz`
- Canonical split projections: `data/vnext_10k/{train,dev,test}.jsonl.gz`
- Nested ordering: `data/vnext_10k/snapshots.json`
- Action-leakage audit: `data/vnext_10k/action_leakage_audit.jsonl.gz`
- Patch report: `reports/vnext_10k_d1_d2_patch.json`
- Matched views:
  `data/vnext_10k/views/{HML_LINEAR,HML_TREE,AST,STRUCTURED_NEUTRAL}/{train,dev,test}.jsonl.gz`

## Execute action

Every EXECUTE input now contains the action that caused the transition.

- All 4,000 Lean rows carry `tactic_text`, copied exactly from the pinned
  LeanDojo trace. It agrees with the canonical transition source and formal
  evidence and carries theorem, trace, transition, revision, and action hashes
  in `audit_metadata.action_provenance`.
- The 24 deterministic synthetic protocol rows carry `action_text` equal to
  their canonical operation and expose their nonempty typed semantic effects.

The exact tactic is legitimate `a_t`. FABLE must not strip it. No action was
generated, paraphrased, inferred from a target, or recovered from later text.
The D1 audit found 4,024 legitimate actions, zero direct target-revealing
actions, zero ambiguous actions, and zero exclusions.

## Model-facing fields

For every arm, FABLE must use only:

- `input_text`: canonical model input string;
- `target_text`: canonical model target string.

Both are strings on all 10,000 rows in every arm. Historical `input` and
`target` object fields are no longer emitted, so there is one authority.

FABLE must not call `json.dumps`, pretty-print or serialize AST/neutral, rebuild
HML, select key order, or otherwise transform representation syntax upstream of
tokenization. `audit_metadata` and task metadata are control-plane fields, not
model inputs.

## Renderer versions

- HML_LINEAR: `hml-linear-state@68178f0+canonical-action-envelope@1.0.0`
- HML_TREE: `hml-tree-state@68178f0+canonical-action-envelope@1.0.0`
- AST: `hmltn-canonical-json-ast@1.0.0`
- STRUCTURED_NEUTRAL: `hmltn-canonical-json-neutral@1.0.0`

AST is canonical compact JSON over the frozen typed AST, with stable keys,
nodes, lists, quoting, escaping, and whitespace. STRUCTURED_NEUTRAL is canonical
compact JSON over the safe neutral input schema. HML_TREE remains a view and has
no facts unavailable to the other arms. Semantic parity is 10,000/10,000.

## Eligibility and membership

- EXECUTE: 4,024 total; train 3,254, dev 392, test 378.
- JUDGE: 6,000.
- REPAIR: 0.
- APPLICABILITY: 0.
- COMPREHENSION: 10,000.

Nested TRAIN∩EXECUTE membership is unchanged: 100→29, 250→81, 1k→326,
5k→1,630, full→3,254. The authoritative overall splits remain train 8,132,
dev 952, test 916. Never resplit atomic rows or resample snapshot rungs.

## Safe-input policy

For `(state_before, action) -> state_after`, use the supplied `input_text` and
`target_text`. Forbidden input remains: `state_after`, target delta, future
claims, final answers, later source-solution text, answer-bearing summaries or
metadata, and renamed direct copies of the target. Actual source action identity
is allowed and required.

The regenerated release passed 10,000/10,000 safe-projection checks and
4,024/4,024 action checks. It found no flagged, ambiguous, or excluded rows.

## Exact regenerated view hashes

| View | Split | SHA-256 |
|---|---:|---|
| HML_LINEAR | train | `e2215950a672bbeba40db6fc881429217e3d305671ab1d17034a6460375e0a70` |
| HML_LINEAR | dev | `b1996172d27a6c97b0d3120633105f90bc76ae5184741a4bd66d8b45a58926c3` |
| HML_LINEAR | test | `4bd9292f6f3b5cb3207a4ed14dcbbec46def87f0f6c7e6e5120b3d33ea09641c` |
| HML_TREE | train | `1d019f2d95da68a41cf414b8c95e61b24ec125fe917d6e7e3a10b3bfd2af9950` |
| HML_TREE | dev | `fb5fa943a7711938d9b0386891758a9284023b14fab3f24bbbdd14a73d2e1285` |
| HML_TREE | test | `659c8ed98908f1cdfb7eddc98cd76968a44b676b2eea765acc483d0a32bd5793` |
| AST | train | `fc9b1dab24dc23c2df8fca5931df0284ee140073b949cbe8732616ee93563571` |
| AST | dev | `4403feb230269d3f95cb83d12abefd4c9373c961d2117b5c201955194abd8d9b` |
| AST | test | `2e18804a3785f756ffc6fd0bf21d3494a915c60a3ac55f399a2b3c7a892e581f` |
| STRUCTURED_NEUTRAL | train | `e456ea9cb7d1d7366e357820ad72d41f057d135b050d8d39b1a62f8addbab029` |
| STRUCTURED_NEUTRAL | dev | `fb570be14d832e07fdb302e0a34d967139c869abe3e0dc2cc94e51466e75eb17` |
| STRUCTURED_NEUTRAL | test | `9c5debc5c3d352e6a4445c5e5a48c2ada8963b625c0b2ff49487ee99851f021d` |

## Next atomic task

FABLE resumes the already-built VNext 10k representation × execution
experiment on the new corpus pin, reruns Phase 0 attestation, and then executes
the unchanged HML_LINEAR vs HML_TREE vs AST vs STRUCTURED_NEUTRAL learning
protocol.
